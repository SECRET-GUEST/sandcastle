#OPENING | https://www.youtube.com/watch?v=_85LaeTCtV8 :3

import subprocess, sys, time, os, importlib, traceback, shutil

import tkinter as tk
from tkinter import filedialog

try:
    from loadingSpinner import Spinner
except Exception:
    class Spinner:
        def loading_start(self, msg): print(msg + "…")
        def loading_stop(self, msg): print(msg)

import numpy as np
import soundfile as sf
from scipy.signal import lfilter, resample_poly

# ================================
# 🔧 Required Libraries
# ================================

REQUIRED_LIBS = ["numpy", "scipy", "soundfile"]

# ================================
# ⚙️ Main Parameters (editable)
# ================================
SAMPLE_RATE = 44100

# Suggestions (voice): delay before first insertion
SUGGEST_DELAY_SEC = 30 * 60   # 30 minutes

# REM Windows (in seconds since falling asleep)
REM_FIRST_START_S   = 75 * 60    # 75 min → 4500 s
REM_WINDOW_LEN_S    = 15 * 60    # window of 15 min (e.g., 75–90 min)
REM_STRIDE_S        = 90 * 60    # new cycle every 90 min

# Suggestions placement (control density / spacing)
REM_PRE_RAMP_S              = 10 * 60   # "ramp" before each REM window where suggestions begin
SUGG_MAX_WINDOW_OCCUPANCY   = 0.12      # max fraction of window occupied by voices (12%)
SUGG_MIN_GAP_BASE_S         = 60        # minimum base gap between two suggestions (s)
SUGG_GAP_FACTOR             = 3.0       # minimum additional gap = voice_duration * factor
SUGG_REUSE_FILES            = True      # True: reuse files if not enough, False: stop when files run out

# Pink noise waves (volume modulation)
PINK_WAVES_WINDOW_SEC  = 30 * 60   # Duration during which waves are applied (here: 30 min)
PINK_WAVE_UP_SEC       = 4         # Rising phase (volume increases)
PINK_WAVE_HOLD_SEC     = 2         # Plateau (volume stable at max)
PINK_WAVE_DOWN_SEC     = 6         # Falling phase (volume decreases)
PINK_WAVE_MIN_AMP      = 0.8       # Minimum volume reached in wave (0 = silence, 0.8 = subtle but present)
PINK_WAVE_MAX_AMP      = 1.0       # Maximum volume reached in wave

# Kick 
KICK_SECTION_SEC  = 30 * 60    # Total duration of kick playback (here: 30 min)
KICK_DECEL_SEC    = 10 * 60    # Duration of tempo deceleration (slowing BPM over 10 min)
KICK_START_BPM    = 60.0       # Starting tempo (beats per minute)
KICK_END_BPM      = 50.0       # Final tempo at end of section
KICK_FADEOUT_SEC  = 30         # Fade-out length for the kick at the end

# Kick sound characteristics
KICK_GAIN_DB    = -8.0     # Overall kick volume (lower = more subtle)
KICK_F_START    = 160.0    # Starting frequency of kick sweep (Hz)
KICK_F_END      = 45.0     # Final frequency reached by the kick (Hz)
KICK_ATTACK_SEC = 0.012    # Attack duration (longer = softer entry)
KICK_DECAY_SEC  = 0.28     # Decay duration (shorter = less resonance)
KICK_H2_DB      = -36.0    # Level of 2nd harmonic (very low here → purer tone)
KICK_DRIVE      = 0.30     # Amount of saturation applied (warmer tone if ↑)
KICK_LPF_HZ     = 220.0    # Low-pass filter applied to kick (smooths highs)
KICK_NORMAL     = 0.8      # Normalization (prevents kick from dominating the mix)

# Voice management (audio suggestions)
DUCK_DB  = -3     # Attenuation applied to background noise while a voice plays
FADE_SEC = 5      # Fade-in/out duration around each voice
VOICE_DB = 6      # Gain applied to voices (relative amplification)

# Pink noise processing
PINK_HPF_HZ = 35.0   # Light high-pass filter to free space in lows (avoids overlap with kick)

# Other utilities
DEBUG = False

# Temporary folder for intermediate files
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/Temp"))

# ================================
# 📦 Dependency Management
# ================================

def install_libs(env_path=None):
    """
    Installs Python libraries listed in requirements.txt.
    - env_path : path to a virtual environment (if provided).
                 If None, installs into the current environment.
    """

    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

    # If a virtual environment path is provided, use its Python executable
    if env_path:
        pip_cmd = [
            os.path.join(env_path, "Scripts", "python"),
            "-m", "pip", "install", "-r", "requirements.txt"
        ]

    subprocess.check_call(pip_cmd)


def create_venv():
    """
    Creates a dedicated virtual environment for the project (./env_sandcastle).
    Returns the path to the created environment.
    """
    env_path = os.path.join(os.getcwd(), "env_sandcastle")
    subprocess.check_call([sys.executable, "-m", "venv", env_path])
    return env_path


def check_libs():
    """
    Checks whether all REQUIRED_LIBS are available.
    Returns a list of missing modules.
    """
    missing = []
    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
        except ImportError:
            missing.append(lib)
    return missing


# ================================
# 📝 Utilities
# ================================

def ask_positive_int(prompt, max_val=None):
    """
    Prompt the user for a positive integer.
    - prompt : displayed text (str)
    - max_val : upper bound (if provided, the value must be strictly less).
    Returns a valid int.
    """
    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                print("❌ Value must be > 0.")
                continue
            if max_val is not None and val >= max_val:
                print(f"❌ Value must be less than {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Please enter a valid integer.")


def db_to_lin(db):
    """
    Converts a gain from decibels (dB) to linear scale.
    Useful for applying volume adjustments or harmonics.
    """
    return 10.0 ** (db / 20.0)


def safe_write_wav(path, data, sr, verbose=True):
    """
    Safely writes a WAV file.
    - path : desired path (extension .wav is enforced if omitted)
    - data : numpy array, mono float32 in [-1, 1]
    - sr   : sample rate (e.g., 44100)
    - verbose : if True, prints success message
    
    Checks folder existence, data validity, and file size.
    """
    if not path or path.strip() == "":
        raise ValueError("Empty output path")

    root, ext = os.path.splitext(path)
    if ext.lower() != ".wav":
        path = root + ".wav"

    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    # Numeric safety (no NaN/Inf)
    if not np.all(np.isfinite(data)):
        bad = (~np.isfinite(data)).sum()
        raise ValueError(f"Non-finite signal (NaN/Inf) in data: {bad} samples")

    # Write
    import soundfile as sf
    sf.write(path, data, sr)

    # Post-write verification
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise IOError(f"Write failed: {path}")

    if verbose:
        print(f"✅ File written: {path} ({os.path.getsize(path)} bytes)")
    return path


def log_stage(name, arr):
    """
    Small debug logger for inspecting an audio signal.
    Prints length and absolute peak if DEBUG=True.
    """
    if not DEBUG:
        return
    import numpy as np
    if arr is None:
        print(f"[{name}] None")
        return
    print(f"[{name}] len={len(arr)} peak={float(np.max(np.abs(arr))):.6f}")


def ensure_temp_dir():
    """
    Ensures that the temporary directory exists,
    then returns its path.
    Used to store intermediate files.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    return TEMP_DIR


def clear_temp_dir():
    """
    Clears the contents of TEMP_DIR.
    Stays silent on failure (only shows a warning if DEBUG=True).
    """
    if os.path.isdir(TEMP_DIR):
        for name in os.listdir(TEMP_DIR):
            p = os.path.join(TEMP_DIR, name)
            try:
                if os.path.isfile(p) or os.path.islink(p):
                    os.remove(p)
                elif os.path.isdir(p):
                    shutil.rmtree(p)
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Unable to remove {p}: {e}")
                # ignored in non-debug mode to keep output clean
                pass


# ================================
# 🎵 Audio utils
# ================================

def smooth_fade_curve(length):
    """
    Generates a smooth fade curve.
    - length : number of samples in the fade
    Returns a vector going from 1 → 0 using a cos² (smooth) curve.
    """
    t = np.linspace(0, np.pi / 2, length)
    return np.cos(t) ** 2


def normalize_audio(data):
    """
    Normalizes an audio signal so its peak reaches ±1.
    """
    peak = np.max(np.abs(data))
    return data / peak if peak > 0 else data


def ensure_mono(data):
    """
    Converts a stereo (or multi-channel) signal to mono
    by averaging the channels.
    """
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data


def one_pole_hp(sig, fc, fs):
    """
    Simple 1-pole high-pass filter.
    - sig : signal
    - fc  : cutoff frequency (Hz)
    - fs  : sample rate (Hz)
    """
    if fc <= 0:
        return sig
    rc = 1.0 / (2 * np.pi * fc)
    alpha = rc / (rc + 1.0 / fs)
    y = np.zeros_like(sig)
    prev_y, prev_x = 0.0, 0.0
    for i, s in enumerate(sig):
        y[i] = alpha * (prev_y + s - prev_x)
        prev_y, prev_x = y[i], s
    return y


def one_pole_lp(sig, fc, fs):
    """
    Simple 1-pole low-pass filter.
    - sig : signal
    - fc  : cutoff frequency (Hz)
    - fs  : sample rate (Hz)
    """
    if fc <= 0:
        return sig
    rc = 1.0 / (2 * np.pi * fc)
    alpha = (1.0 / fs) / (rc + 1.0 / fs)
    y = np.zeros_like(sig)
    prev = 0.0
    for i, s in enumerate(sig):
        prev = prev + alpha * (s - prev)
        y[i] = prev
    return y


def compute_rem_windows(total_seconds,
                        first_start_s=REM_FIRST_START_S,
                        window_len_s=REM_WINDOW_LEN_S,
                        stride_s=REM_STRIDE_S):
    """
    Computes the REM windows covered by the total duration.
    Returns a list of tuples (start_s, end_s).
    """
    windows = []
    s = first_start_s
    while s < total_seconds:
        e = min(s + window_len_s, total_seconds)
        if e > s:
            windows.append((s, e))
        s += stride_s
    return windows


# ================================
# 🎵 Audio Suggests
# ================================


def _resample_to_target(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    """High-quality resample using polyphase filtering (no extra deps)."""
    if sr_in == sr_out:
        return x
    # Use integer ratio for best quality
    from math import gcd
    g = gcd(sr_in, sr_out)
    up = sr_out // g
    down = sr_in // g
    # resample_poly expects shape (n,) or (n, ch). We’re mono before calling.
    y = resample_poly(x, up, down, padtype="line")  # default Kaiser window
    return y.astype(np.float32, copy=False)


def _ensure_mono_float32(x: np.ndarray) -> np.ndarray:
    """Convert to mono float32 in [-1, 1]."""
    if x.ndim == 2:
        x = np.mean(x, axis=1)
    x = x.astype(np.float32, copy=False)
    return x

def load_audio_any(fpath: str, target_sr: int):
    """
    Try to read WAV/MP3 with soundfile.
    Returns (audio_mono_f32, sr_out) where sr_out==target_sr, or (None, None) on failure.
    """
    try:
        # always_2d=False gives (n,) for mono, (n, ch) for stereo
        data, sr = sf.read(fpath, always_2d=False)
    except Exception as e:
        print(f"⚠️ Impossible de lire {os.path.basename(fpath)} : {e}")
        return None, None

    # To mono float32
    data = _ensure_mono_float32(data)

    # Normalize *softly* to prevent clipping and keep levels consistent
    # (assumes you already have normalize_audio; fall back to simple norm if not)
    try:
        data = normalize_audio(data)
    except NameError:
        peak = np.max(np.abs(data)) or 1.0
        data = (data / peak) * 0.95

    # Resample if needed
    data = _resample_to_target(data, sr, target_sr)
    return data, target_sr




def integrate_suggestions(pink_noise, sample_rate, total_duration, start_delay_sec):
    """
    Places audio suggestions while respecting:
      - No insertion before `start_delay_sec` (e.g., ≥ 30 min)
      - 1st REM: density increases toward the end of the window
      - Subsequent REMs: controlled random placement (uniform)
      - Max window occupancy (SUGG_MAX_WINDOW_OCCUPANCY)
      - Minimum gap between suggestions 
        (SUGG_MIN_GAP_BASE_S + voice_length * SUGG_GAP_FACTOR)
    """

    suggest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
    if not os.path.isdir(suggest_path):
        print("⚠️ Suggestions folder not found:", suggest_path)
        return pink_noise

    # Accepts both WAV and MP3
    file_names = [f for f in os.listdir(suggest_path) if f.lower().endswith((".wav", ".mp3"))]
    if not file_names:
        print("⚠️ No suggestion files found.")
        return pink_noise

    # Full paths (loaded on demand)
    file_paths = [os.path.join(suggest_path, f) for f in file_names]

    total_samples = int(total_duration * sample_rate)

    # REM windows
    rem_windows = compute_rem_windows(total_duration)
    if not rem_windows:
        print("ℹ️ Duration too short: no REM windows covered.")
        return pink_noise

    rng = np.random.default_rng()

    # Iterate over REM windows
    for w_idx, (rem_start_s, rem_end_s) in enumerate(rem_windows):
        # Influence window = pre-ramp + REM itself
        # Clamped by start_delay_sec and total duration.
        w_start_s = max(rem_start_s - REM_PRE_RAMP_S, start_delay_sec)
        w_end_s   = min(rem_end_s, total_duration)
        if w_end_s <= w_start_s:
            continue

        win_len_s   = w_end_s - w_start_s
        occ_limit_s = win_len_s * SUGG_MAX_WINDOW_OCCUPANCY

        # Randomized file order (reused if SUGG_REUSE_FILES=True)
        order = np.arange(len(file_paths))
        rng.shuffle(order)

        used_time_s = 0.0
        placed_intervals = []  # list of (start_s, end_s) for this window

        # Draw insertion time (biased toward end for 1st REM)
        def draw_time(start_s, end_s, voice_len_s, towards_end):
            lo = start_s
            hi = max(start_s, end_s - voice_len_s)
            if hi <= lo:
                return None
            u = rng.random()
            if towards_end:
                # Quadratic bias toward the END (close to 1)
                u = 1 - (1 - u)**2
            return lo + (hi - lo) * u


        passes = 0
        max_passes = 3 if SUGG_REUSE_FILES else 1

        while used_time_s < occ_limit_s and passes < max_passes:
            for idx in order:
                fpath = file_paths[idx]
                # ✅ Universal loader with auto-resampling to target `sample_rate`
                voice_data, _sr = load_audio_any(fpath, sample_rate)
                if voice_data is None:
                    # MP3 not supported by libsndfile → skip gracefully
                    if fpath.lower().endswith(".mp3"):
                        print(f"⚠️ {os.path.basename(fpath)} ignored (MP3 not supported by your libsndfile).")
                    continue
                
                voice_len_s = len(voice_data) / sample_rate

                # Window occupancy limit
                if used_time_s + voice_len_s > occ_limit_s:
                    continue

                # 1st REM → progressive accumulation toward end; otherwise uniform
                towards_end = (w_idx == 0)
                t_s = draw_time(w_start_s, w_end_s, voice_len_s, towards_end=towards_end)
                if t_s is None:
                    continue

                # Minimal gap = base + proportional to voice duration
                min_gap = SUGG_MIN_GAP_BASE_S + voice_len_s * SUGG_GAP_FACTOR
                ok = True
                for (a, b) in placed_intervals:
                    if not (t_s - min_gap >= b or (t_s + voice_len_s) + min_gap <= a):
                        ok = False
                        break
                if not ok:
                    continue

                # Sample conversion + bounds for ducking
                insert = int(t_s * sample_rate)
                fade_samp = int(FADE_SEC * sample_rate)
                if insert < 0 or insert + len(voice_data) + fade_samp + 1 >= total_samples:
                    continue

                # Apply ducking + mix in voice
                pink_noise = apply_ducking(pink_noise, voice_data, insert, sample_rate)

                # Update state
                placed_intervals.append((t_s, t_s + voice_len_s))
                used_time_s += voice_len_s

                if used_time_s >= occ_limit_s * 0.98:
                    break

            passes += 1

        if DEBUG:
            print(f"[REM {w_idx+1}] start={w_start_s:.0f}s end={w_end_s:.0f}s "
                  f"used≈{used_time_s:.1f}s (limit {occ_limit_s:.1f}s), "
                  f"suggestions={len(placed_intervals)}")

    return pink_noise

# ================================
# 🎵 Kick
# ================================

def synth_one_kick(sample_rate=SAMPLE_RATE, dur_sec=0.6,
                   f_start=KICK_F_START, f_end=KICK_F_END,
                   attack_sec=KICK_ATTACK_SEC, decay_sec=KICK_DECAY_SEC,
                   add_h2_db=KICK_H2_DB, drive=KICK_DRIVE):
    """
    Generates a single synthetic kick hit.
    Inspired by "Weightless-like" kicks: soft, deep, rounded.

    - sample_rate : sampling rate (Hz)
    - dur_sec     : total duration of the kick (s)
    - f_start     : starting frequency of the pitch envelope (Hz)
    - f_end       : final frequency (Hz)
    - attack_sec  : attack duration (s) → gradual fade-in
    - decay_sec   : release duration (s)
    - add_h2_db   : level of the 2nd harmonic (dB)
    - drive       : soft saturation intensity (0 → clean, 1 → strong)

    Returns: normalized numpy.float32 array (kick signal).
    """
    n = int(dur_sec * sample_rate)
    t = np.arange(n) / sample_rate

    # Pitch envelope (smooth exponential drop)
    k = np.log(f_end / f_start) / max(1e-9, dur_sec)
    f_t = f_start * np.exp(k * t)
    phase = 2 * np.pi * np.cumsum(f_t) / sample_rate

    # Base signal: sine + 2nd harmonic
    base  = np.sin(phase)
    harm2 = np.sin(2 * phase) * db_to_lin(add_h2_db)

    # Amplitude envelope (attack + decay)
    env = np.ones_like(t)
    a_n = int(max(1, attack_sec * sample_rate))
    env[:a_n] = np.linspace(0.0, 1.0, a_n, endpoint=False)  # attack
    env[a_n:] = np.linspace(1.0, 0.0, len(t) - a_n)         # decay

    # Apply envelope + saturation
    x = (base + harm2) * env
    x = np.tanh(x * (1.0 + drive))          # soft saturation
    x = one_pole_hp(x, 20.0, sample_rate)   # cut subsonics (<20Hz)
    x = one_pole_lp(x, KICK_LPF_HZ, sample_rate)  # smooth highs

    # Internal normalization
    peak = np.max(np.abs(x)) + 1e-9
    x = x / peak

    # Global kick gain
    x *= db_to_lin(KICK_GAIN_DB)
    return x.astype(np.float32)


def build_kick_track(total_len_samples, sample_rate=SAMPLE_RATE):
    """
    Builds the full kick track over the entire duration.
    - Respects kick section length + BPM deceleration + final fade-out.

    - total_len_samples : total length of the track (samples)
    - sample_rate       : sampling rate (Hz)

    Returns: numpy.float32 array containing the kick sequence.
    """
    # Kick section duration
    section_samples = int(min(KICK_SECTION_SEC, total_len_samples / sample_rate) * sample_rate)
    kick_track = np.zeros(total_len_samples, dtype=np.float32)

    # Generate one single kick
    one_kick = synth_one_kick(sample_rate=sample_rate)

    # Place hits following a decreasing BPM
    t_sec = 0.0
    end_sec = section_samples / sample_rate
    while t_sec < end_sec:
        # Progressive BPM slowdown
        if t_sec < KICK_DECEL_SEC:
            p = t_sec / max(1e-9, KICK_DECEL_SEC)
            bpm = KICK_START_BPM + (KICK_END_BPM - KICK_START_BPM) * p
        else:
            bpm = KICK_END_BPM

        # Place hit
        period = 60.0 / bpm
        idx = int(t_sec * sample_rate)
        end_idx = min(idx + len(one_kick), total_len_samples)
        seg = one_kick[:end_idx - idx]
        kick_track[idx:end_idx] += seg

        t_sec += period

    # Fade-out at the end of the section
    fade_samples = int(min(KICK_FADEOUT_SEC, end_sec) * sample_rate)
    if fade_samples > 0:
        start = int(end_sec * sample_rate) - fade_samples
        start = max(0, start)
        fade = np.linspace(1.0, 0.0, fade_samples).astype(np.float32)
        kick_track[start:start+fade_samples] *= fade

    # Gentle normalization with headroom
    peak = np.max(np.abs(kick_track))
    if peak > 0:
        kick_track = KICK_NORMAL * (kick_track / peak)

    return kick_track

# ================================
# 🎵 Pink noise + mix generation
# ================================

def apply_ducking(pink_noise, voice, start_sample, sample_rate):
    """
    Applies ducking: attenuates pink noise to make space for inserted voice.
    - pink_noise   : pink noise signal
    - voice        : voice signal
    - start_sample : insertion position (samples)
    - sample_rate  : sampling rate
    """
    fade_samples = int(FADE_SEC * sample_rate)
    end_sample = start_sample + len(voice)

    # Safety: avoid overflow beyond pink noise length
    if end_sample + fade_samples > len(pink_noise):
        end_sample = len(pink_noise) - fade_samples

    # Fade curve around voice
    fade_curve = smooth_fade_curve(fade_samples)
    sustain_gain = db_to_lin(DUCK_DB)   # background attenuation
    voice_gain   = db_to_lin(VOICE_DB)  # voice amplification

    # Progressive fade before voice
    pink_noise[start_sample:start_sample+fade_samples] *= (
        fade_curve * (1 - sustain_gain) + sustain_gain
    )
    # Constant attenuation during voice
    pink_noise[start_sample+fade_samples:end_sample] *= sustain_gain
    # Progressive return after voice
    pink_noise[end_sample:end_sample+fade_samples] *= (
        fade_curve[::-1] * (1 - sustain_gain) + sustain_gain
    )

    # Add voice
    pink_noise[start_sample:end_sample] += voice * voice_gain
    return pink_noise


def build_pink_waves_envelope(total_len_samples, sr):
    """
    1D envelope to modulate pink noise in wave-like patterns.
    """
    window_samples = int(min(PINK_WAVES_WINDOW_SEC, total_len_samples / sr) * sr)
    if window_samples <= 0:
        return np.ones(total_len_samples, dtype=np.float32)

    upN   = max(1, int(PINK_WAVE_UP_SEC   * sr))
    holdN = max(1, int(PINK_WAVE_HOLD_SEC * sr))
    downN = max(1, int(PINK_WAVE_DOWN_SEC * sr))

    # Smooth curves: rise = inverted fade, fall = normal fade
    up   = smooth_fade_curve(upN)[::-1]                  # 0 -> 1
    hold = np.ones(holdN, dtype=np.float32)              # 1
    down = smooth_fade_curve(downN)                      # 1 -> 0

    cycle = np.concatenate([up, hold, down]).astype(np.float32)

    # Scale between MIN and MAX
    amp_min, amp_max = PINK_WAVE_MIN_AMP, PINK_WAVE_MAX_AMP
    cycle = amp_min + (amp_max - amp_min) * cycle

    # Repeat cycle to cover window
    reps = window_samples // len(cycle) + 1
    env_section = np.tile(cycle, reps)[:window_samples]

    # Global envelope = env_section (window 30 min), then 1.0
    env = np.ones(total_len_samples, dtype=np.float32)
    env[:window_samples] = env_section
    return env


# ================================
# 🚀 Main script
# ================================



def main_generate(total_duration, fade_out, save_path, kick_enabled=True, waves_enabled=True):
    """
    Generates the full audio track (pink noise + waves + kick + voices).

    Steps:
    1. Generate white noise → filter into pink noise
    2. Apply optional wave modulation (breathing effect)
    3. Generate kick track + mix
    4. Apply final fade-out
    5. Insert vocal suggestions with ducking
    6. Normalize final mix
    7. Save intermediate files (debug) + final file

    - total_duration : total render duration (s)
    - fade_out       : fade-out duration (s)
    - save_path      : output .wav file path
    - kick_enabled   : enable/disable kick track
    - waves_enabled  : enable/disable wave effect
    """
    sample_rate = 44100
    samples = total_duration * sample_rate

    # 1. White noise → pink noise
    white = np.random.normal(0, 1, samples).astype(np.float32)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    pink = lfilter(b, a, white).astype(np.float32)
    pink /= (np.max(np.abs(pink)) + 1e-9)

    # 2. Wave modulation (if enabled)
    if waves_enabled:
        env = build_pink_waves_envelope(len(pink), sample_rate)
        pink *= env
    log_stage("pink", pink)

    # 3. Kick generation + mix (if enabled)
    if kick_enabled:
        kick = build_kick_track(len(pink), sample_rate)
        log_stage("kick", kick)
        mix = pink + kick
    else:
        kick = np.zeros_like(pink)  # placeholder for debug
        mix = pink
    log_stage("mix_before_suggest", mix)

    # 4. Final fade-out (optional)
    if fade_out > 0:
        fN = fade_out * sample_rate
        fade = np.linspace(1, 0, fN, dtype=np.float32)
        mix[-fN:] *= fade
        log_stage("mix_after_fade", mix)

    # 5. Insert vocal suggestions
    mix = integrate_suggestions(mix, sample_rate, total_duration,
                                start_delay_sec=SUGGEST_DELAY_SEC)
    log_stage("mix_after_suggest", mix)

    # 6. Final normalization (≈2% headroom)
    peak = np.max(np.abs(mix))
    if peak > 1e-9:
        mix = 0.98 * (mix / peak)
    log_stage("final", mix)

    # 7. Save files (intermediates + final)
    temp_dir = ensure_temp_dir()
    try:
        # Intermediate files (debug only)
        safe_write_wav(os.path.join(temp_dir, "_pink.wav"), pink, sample_rate, verbose=False)
        safe_write_wav(os.path.join(temp_dir, "_kick.wav"), kick, sample_rate, verbose=False)
        safe_write_wav(os.path.join(temp_dir, "_mix_before_suggest.wav"), mix, sample_rate, verbose=False)

        # Final file (with log visible)
        safe_write_wav(save_path, mix.astype(np.float32), sample_rate)
    finally:
        # Cleanup TEMP_DIR
        clear_temp_dir()



if __name__ == "__main__":
    """
    Script entry point:
    1. Check dependencies
    2. Manage venv creation or global install
    3. Get total duration, fade-out + kick/waves options
    4. Launch UI to choose save path
    5. Generate final mix (pink noise + kick + options)
    """
    print("🔍 Checking dependencies…")
    if "--skip-setup" not in sys.argv:
        missing_libs = check_libs()
        if missing_libs:
            print(f"⚠️ Missing libraries: {', '.join(missing_libs)}")
            choice = input("Create a virtual environment (V) or install globally (G)? [V/G]: ").strip().lower()
            if choice == "v":
                env_path = create_venv()
                install_libs(env_path)
                python_exec = os.path.join(env_path, "Scripts", "python")
                subprocess.check_call([python_exec, __file__, "--skip-setup"] + sys.argv[1:])
                sys.exit()
            else:
                install_libs()
                subprocess.check_call([sys.executable, __file__, "--skip-setup"] + sys.argv[1:])
                sys.exit()
        else:
            print("✅ All libraries already installed.\n")

    # 2. CLI params or user input
    kick_enabled = True
    waves_enabled = True

    if len(sys.argv) >= 3:
        try:
            total_duration = int(sys.argv[1])
            fade_out = int(sys.argv[2])

            # Optional: kick + waves flags
            if len(sys.argv) >= 5:
                kick_enabled = bool(int(sys.argv[3]))
                waves_enabled = bool(int(sys.argv[4]))

            if total_duration <= 0 or fade_out < 0 or fade_out >= total_duration:
                raise ValueError
        except ValueError:
            total_duration = ask_positive_int("Total duration (seconds): ")
            fade_out = ask_positive_int("Fade-out (seconds): ", max_val=total_duration)
    else:
        total_duration = ask_positive_int("Total duration (seconds): ")
        fade_out = ask_positive_int("Fade-out (seconds): ", max_val=total_duration)

    # 3. Spinner feedback
    spinner = Spinner()
    spinner.loading_start("Generating mix (pink noise + kick + options)")

    # 4. File save UI
    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        title="Save audio file",
        initialfile="sleepy_pinknoise.wav"
    )

    # 5. Generate or cancel
    if save_path:
        try:
            main_generate(total_duration, fade_out, save_path, kick_enabled, waves_enabled)
            spinner.loading_stop("Audio generated")
            print(f"File path: {os.path.abspath(save_path)}")
        except Exception as e:
            spinner.loading_stop("Error during generation")
            print("❌ Exception:", e)
            traceback.print_exc()
        finally:
            time.sleep(1)
            sys.exit()
    else:
        spinner.loading_stop("Save cancelled")
        time.sleep(1)
        sys.exit()



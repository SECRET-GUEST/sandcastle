import subprocess, sys, time, os, importlib
import tkinter as tk
from tkinter import filedialog
from loadingSpinner import Spinner
import numpy as np
import soundfile as sf
from scipy.signal import lfilter

# ================================
# 🔧 Required libraries
# ================================
REQUIRED_LIBS = ["numpy", "scipy", "soundfile"]

# ================================
# 📦 Dependency management
# ================================
def install_libs(env_path=None):
    """Install necessary libraries (either in venv or globally)"""
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    if env_path:
        pip_cmd = [os.path.join(env_path, "Scripts", "python"), "-m", "pip", "install", "-r", "requirements.txt"]
    subprocess.check_call(pip_cmd)

def create_venv():
    """Create a virtual environment for the project"""
    env_path = os.path.join(os.getcwd(), "env_sandcastle")
    subprocess.check_call([sys.executable, "-m", "venv", env_path])
    return env_path

def check_libs():
    """Check if all required libraries are installed"""
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
    """Ask the user for a positive integer with validation"""
    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                print("❌ Value must be greater than 0.")
                continue
            if max_val is not None and val >= max_val:
                print(f"❌ Value must be less than {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Please enter a valid integer.")

# ================================
# 🎛 Audio processing
# ================================

DUCK_DB = -3       # Gentle attenuation of pink noise during voice
FADE_SEC = 5       # Fade in/out duration in seconds
VOICE_DB = 6       # Gain applied to voice for clarity

def smooth_fade_curve(length):
    """Generate a smooth cos² fade curve"""
    t = np.linspace(0, np.pi / 2, length)
    return np.cos(t)**2  # Smooth decay

def normalize_audio(data):
    """Normalize audio signal (works for mono or stereo)"""
    max_val = np.max(np.abs(data))
    return data / max_val if max_val > 0 else data

def ensure_mono(data):
    """Convert audio to mono if it's stereo"""
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data

def apply_ducking(pink_noise, voice, start_sample, sample_rate):
    """Apply ultra-smooth ducking without abrupt volume changes"""
    fade_samples = int(FADE_SEC * sample_rate)
    end_sample = start_sample + len(voice)

    # Safety: bounds check
    if end_sample + fade_samples > len(pink_noise):
        end_sample = len(pink_noise) - fade_samples

    # Smooth curves
    fade_curve = smooth_fade_curve(fade_samples)
    sustain_gain = 10**(DUCK_DB / 20)
    voice_gain = 10**(VOICE_DB / 20)

    # 🔹 1. Fade out pink noise before voice
    pink_noise[start_sample:start_sample+fade_samples] *= (
        fade_curve * (1 - sustain_gain) + sustain_gain
    )

    # 🔹 2. Keep pink noise attenuated during voice playback
    pink_noise[start_sample+fade_samples:end_sample] *= sustain_gain

    # 🔹 3. Fade in pink noise after voice
    pink_noise[end_sample:end_sample+fade_samples] *= (
        fade_curve[::-1] * (1 - sustain_gain) + sustain_gain
    )

    # 🔹 4. Add the voice track
    pink_noise[start_sample:end_sample] += voice * voice_gain

    return pink_noise

def integrate_suggestions(pink_noise, sample_rate, total_duration):
    """Integrate voice suggestions spaced intelligently throughout the audio"""
    suggest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
    files = [f for f in os.listdir(suggest_path) if f.endswith(".wav")]

    if not files:
        print("⚠️ No suggestion files found.")
        return pink_noise

    total_samples = total_duration * sample_rate
    interval = total_samples // (len(files) + 1)  # Even spacing

    for i, filename in enumerate(files):
        voice_path = os.path.join(suggest_path, filename)
        voice_data, sr = sf.read(voice_path)

        # Check sample rate
        if sr != sample_rate:
            print(f"⚠️ {filename} skipped (wrong sample rate).")
            continue

        # Prepare voice track
        voice_data = ensure_mono(voice_data)
        voice_data = normalize_audio(voice_data)

        # Calculate insertion position
        start_sample = (i + 1) * interval
        pink_noise = apply_ducking(pink_noise, voice_data, start_sample, sample_rate)

    return pink_noise

# ================================
# 🎵 Pink noise generation
# ================================
def main_generate(total_duration, fade_out, save_path):
    sample_rate = 44100
    samples = total_duration * sample_rate

    # Generate white noise
    white_noise = np.random.normal(0, 1, samples).astype(np.float32)

    # Filter to pink noise
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    pink_noise = lfilter(b, a, white_noise)
    pink_noise /= np.max(np.abs(pink_noise))

    # Apply global fade-out if defined
    if fade_out > 0:
        fade_samples = fade_out * sample_rate
        fade_curve = np.linspace(1, 0, fade_samples)
        pink_noise[-fade_samples:] *= fade_curve

    # Integrate suggestions
    pink_noise = integrate_suggestions(pink_noise, sample_rate, total_duration)

    # Save file
    if save_path:
        sf.write(save_path, pink_noise, sample_rate)

# ================================
# 🚀 Main script
# ================================
if __name__ == "__main__":
    print("🔍 Checking dependencies...")

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
            print("✅ All required libraries are already installed.\n")

    if len(sys.argv) >= 3:
        try:
            total_duration = int(sys.argv[1])
            fade_out = int(sys.argv[2])
            if total_duration <= 0 or fade_out < 0 or fade_out >= total_duration:
                raise ValueError
        except ValueError:
            total_duration = ask_positive_int("Total duration in seconds: ")
            fade_out = ask_positive_int("Fade-out duration in seconds: ", max_val=total_duration)
    else:
        total_duration = ask_positive_int("Total duration in seconds: ")
        fade_out = ask_positive_int("Fade-out duration in seconds: ", max_val=total_duration)

    spinner = Spinner()
    spinner.loading_start("Generating pink noise")

    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")], title="Save pink noise", initialfile="pink_noise_filtered.wav")

    if save_path:
        main_generate(total_duration, fade_out, save_path)
        spinner.loading_stop("Sound generated")
        print(f"File saved to: {save_path}\n")
        time.sleep(1)
        sys.exit()
    else:
        spinner.loading_stop("Save canceled")
        time.sleep(1)
        sys.exit()

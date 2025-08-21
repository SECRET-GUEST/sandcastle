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
# 🔧 Librairies requises
# ================================

REQUIRED_LIBS = ["numpy", "scipy", "soundfile"]

# ================================
# ⚙️ Paramètres principaux (modifiables)
# ================================
SAMPLE_RATE = 44100

# Suggestions (voix) : retard avant la 1ère insertion
SUGGEST_DELAY_SEC = 30 * 60   # 30 minutes

# Fenêtres REM (en secondes depuis l'endormissement)
REM_FIRST_START_S   = 75 * 60    # 75 min → 4500 s
REM_WINDOW_LEN_S    = 15 * 60    # fenêtre de 15 min (ex: 75–90 min)
REM_STRIDE_S        = 90 * 60    # nouveau cycle toutes les 90 min

# Placement des suggestions (contrôle densité/écarts) 
REM_PRE_RAMP_S              = 10 * 60   # "rampe" avant chaque fenêtre REM où on commence à placer des suggestions
SUGG_MAX_WINDOW_OCCUPANCY   = 0.12      # part max de la fenêtre occupée par des voix (12%)
SUGG_MIN_GAP_BASE_S         = 60        # écart minimal de base entre deux suggestions (s)
SUGG_GAP_FACTOR             = 3.0       # écart minimal additionnel = durée_voix * facteur
SUGG_REUSE_FILES            = True      # True: on réutilise les fichiers si on en manque, False: on s'arrête

# Vagues de bruit rose (modulation du volume)
PINK_WAVES_WINDOW_SEC  = 30 * 60   # Durée pendant laquelle les vagues sont appliquées (ici : 30 min)
PINK_WAVE_UP_SEC       = 4         # Temps de montée progressive (volume qui grimpe)
PINK_WAVE_HOLD_SEC     = 2         # Temps de plateau (volume stable au max)
PINK_WAVE_DOWN_SEC     = 6         # Temps de descente progressive (volume qui redescend)
PINK_WAVE_MIN_AMP      = 0.8       # Volume minimum atteint dans la vague (0 = silence complet, 0.8 = discret mais toujours présent)
PINK_WAVE_MAX_AMP      = 1.0       # Volume maximum atteint dans la vague

# Kick 
KICK_SECTION_SEC  = 30 * 60    # Durée totale pendant laquelle le kick est joué (ici : 30 min)
KICK_DECEL_SEC    = 10 * 60    # Durée de la décélération progressive du tempo (baisse du BPM sur 10 min)
KICK_START_BPM    = 60.0       # Tempo de départ en battements par minute
KICK_END_BPM      = 50.0       # Tempo d’arrivée en battements par minute
KICK_FADEOUT_SEC  = 30         # Durée du fondu de sortie du kick à la fin de la section

# Caractéristiques sonores du kick
KICK_GAIN_DB    = -8.0     # Volume global du kick (plus bas = plus discret)
KICK_F_START    = 160.0    # Fréquence de départ de la descente du kick (Hz)
KICK_F_END      = 45.0     # Fréquence finale atteinte par le kick (Hz)
KICK_ATTACK_SEC = 0.012    # Durée de l’attaque (plus long = entrée plus douce)
KICK_DECAY_SEC  = 0.28     # Durée de la décroissance (plus court = moins de résonance/rebond)
KICK_H2_DB      = -36.0    # Niveau de la 2ᵉ harmonique (très faible ici → son plus pur)
KICK_DRIVE      = 0.30     # Quantité de saturation appliquée (colore le son, plus chaud si ↑)
KICK_LPF_HZ     = 220.0    # Filtre passe-bas appliqué au kick (arrondit le son en coupant les aigus)
KICK_NORMAL     = 0.8      # Normalisation (ajuste pour éviter que le kick ne domine le mix)


# Gestion des voix (suggestions audio)
DUCK_DB  = -3     # Atténuation appliquée au bruit de fond quand une voix est jouée
FADE_SEC = 5      # Durée du fondu d’entrée/sortie autour de chaque voix
VOICE_DB = 6      # Gain appliqué aux voix (amplification relative)


# Traitement du bruit rose
PINK_HPF_HZ = 35.0   # Filtre passe-haut léger pour libérer de l’espace dans les basses (évite que le kick et le bruit rose se marchent dessus)


# Autres utilitaires

DEBUG = False

# Dossier temporaire pour les fichiers intermédiaires
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/Temp"))


# ================================
# 📦 Gestion des dépendances
# ================================

def install_libs(env_path=None):

    """

    Installe les librairies Python listées dans requirements.txt.
    - env_path : chemin vers un environnement virtuel (si fourni).
                 Si None, installation dans l’environnement courant.

    """

    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

    # Si un chemin d'environnement virtuel est fourni, on utilise son exécutable Python
    if env_path:
        pip_cmd = [
            os.path.join(env_path, "Scripts", "python"),
            "-m", "pip", "install", "-r", "requirements.txt"
        ]

    subprocess.check_call(pip_cmd)


def create_venv():

    """

    Crée un environnement virtuel dédié au projet (./env_sandcastle).
    Retourne le chemin de l'environnement créé.

    """

    env_path = os.path.join(os.getcwd(), "env_sandcastle")
    subprocess.check_call([sys.executable, "-m", "venv", env_path])
    return env_path


def check_libs():

    """

    Vérifie si toutes les librairies de REQUIRED_LIBS sont disponibles.
    Retourne une liste des modules manquants.

    """

    missing = []
    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
        except ImportError:
            missing.append(lib)
    return missing


# ================================
# 📝 Utilitaires
# ================================

def ask_positive_int(prompt, max_val=None):

    """

    Demande un entier positif à l'utilisateur.
    - prompt : texte affiché (str)
    - max_val : valeur STRICTEMENT supérieure interdite (si fournie).
    Retourne un int valide.

    """

    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                print("❌ La valeur doit être > 0.")
                continue
            if max_val is not None and val >= max_val:
                print(f"❌ La valeur doit être inférieure à {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Entrez un nombre entier valide.")


def db_to_lin(db):

    """

    Convertit un gain en décibels (dB) vers un gain linéaire.
    Utile pour appliquer des réglages de volume ou d’harmoniques.

    """

    return 10.0 ** (db / 20.0)


def safe_write_wav(path, data, sr, verbose=True):

    """

    Écrit un fichier WAV de façon sécurisée.
    - path : chemin souhaité (l’extension .wav est forcée si omise)
    - data : numpy array mono float32 dans [-1, 1]
    - sr   : sample rate (ex: 44100)
    - verbose : si True, affiche un message de succès
    Vérifie l’existence du dossier, la validité numérique des données, et la taille du fichier écrit.

    """

    if not path or path.strip() == "":
        raise ValueError("Chemin de sortie vide")

    root, ext = os.path.splitext(path)
    if ext.lower() != ".wav":
        path = root + ".wav"

    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    # Garde-fous numériques (pas de NaN/Inf)
    if not np.all(np.isfinite(data)):
        bad = (~np.isfinite(data)).sum()
        raise ValueError(f"Signal non-fini (NaN/Inf) dans les données: {bad} échantillons")

    # Écriture
    import soundfile as sf
    sf.write(path, data, sr)

    # Vérification post-écriture
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise IOError(f"Échec d'écriture: {path}")

    if verbose:
        print(f"✅ Fichier écrit: {path} ({os.path.getsize(path)} octets)")
    return path


def log_stage(name, arr):

    """

    Petit logger de debug pour inspecter un signal audio.
    Affiche la longueur et le pic absolu si DEBUG=True.

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

    S’assure que le dossier temporaire existe, puis retourne son chemin.
    Utilisé pour stocker d’éventuels fichiers intermédiaires.

    """

    os.makedirs(TEMP_DIR, exist_ok=True)
    return TEMP_DIR


def clear_temp_dir():

    """

    Vide le contenu du dossier temporaire TEMP_DIR.
    Reste silencieux en cas d’échec (affiche un warning seulement si DEBUG=True).

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
                    print(f"⚠️ Impossible de supprimer {p}: {e}")
                # on ignore en mode non-debug pour ne pas polluer la sortie
                pass


# ================================
# 🎛 Audio utils
# ================================

def smooth_fade_curve(length):

    """

    Génère une courbe de fondu (fade) douce.
    - length : nombre d’échantillons du fondu
    Retourne un vecteur entre 1 → 0 avec une courbe cos² (smooth).

    """

    t = np.linspace(0, np.pi / 2, length)
    return np.cos(t)**2


def normalize_audio(data):

    """

    Normalise un signal audio pour que son pic atteigne ±1.

    """

    peak = np.max(np.abs(data))
    return data / peak if peak > 0 else data


def ensure_mono(data):

    """

    Convertit un signal stéréo (ou multi-canaux) en mono
    en moyennant les canaux.

    """

    if data.ndim > 1:
        data = data.mean(axis=1)
    return data


def one_pole_hp(sig, fc, fs):

    """

    Filtre passe-haut simple à 1 pôle.
    - sig : signal
    - fc  : fréquence de coupure (Hz)
    - fs  : fréquence d’échantillonnage (Hz)

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

    Filtre passe-bas simple à 1 pôle.
    - sig : signal
    - fc  : fréquence de coupure (Hz)
    - fs  : fréquence d’échantillonnage (Hz)

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
    Calcule les fenêtres REM couvertes par la durée totale.
    Retourne une liste de tuples (start_s, end_s).
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
# 🎛 Suggestions audio
# ================================

def _resample_to_target(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    """
    Rééchantillonne `x` de sr_in → sr_out avec filtrage polyphasé.
    - Préserve une bonne qualité (fenêtre de Kaiser par défaut).
    """
    if sr_in == sr_out:
        return x
    from math import gcd
    g = gcd(sr_in, sr_out)
    up = sr_out // g
    down = sr_in // g
    return resample_poly(x, up, down, padtype="line").astype(np.float32, copy=False)



def _ensure_mono_float32(x: np.ndarray) -> np.ndarray:
    """
    Convertit le signal en :
      - mono (moyenne des canaux si stéréo),
      - float32 normalisé [-1, 1].
    """
    if x.ndim == 2:
        x = np.mean(x, axis=1)
    return x.astype(np.float32, copy=False)

def load_audio_any(fpath: str, target_sr: int):
    """
    Charge un fichier audio (WAV ou MP3 si supporté par libsndfile).
    Étapes :
      - Lecture avec soundfile
      - Conversion en mono float32
      - Normalisation
      - Rééchantillonnage à `target_sr` si besoin
    Retourne (signal, target_sr) ou (None, None) si échec.
    """
    try:
        data, sr = sf.read(fpath, always_2d=False)
    except Exception as e:
        print(f"⚠️ Impossible de lire {os.path.basename(fpath)} : {e}")
        return None, None

    # → Mono + float32
    data = _ensure_mono_float32(data)

    # → Normalisation
    try:
        data = normalize_audio(data)
    except NameError:
        peak = np.max(np.abs(data)) or 1.0
        data = (data / peak) * 0.95

    # → Rééchantillonnage
    data = _resample_to_target(data, sr, target_sr)
    return data, target_sr


def integrate_suggestions(pink_noise, sample_rate, duree_totale, start_delay_sec):
    """
    Place des suggestions audio en respectant :
      - Aucune insertion avant `start_delay_sec` (ex : ≥ 30 min)
      - 1ʳᵉ REM : densité qui augmente en s'approchant de la fin de fenêtre
      - REM suivantes : placement aléatoire contrôlé (uniforme)
      - Occupation max de chaque fenêtre (SUGG_MAX_WINDOW_OCCUPANCY)
      - Écart minimal entre suggestions (SUGG_MIN_GAP_BASE_S + durée * SUGG_GAP_FACTOR)
    """
    suggest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
    if not os.path.isdir(suggest_path):
        print("⚠️ Dossier de suggestions introuvable :", suggest_path)
        return pink_noise

    # ✅ Accepte WAV et MP3
    file_names = [f for f in os.listdir(suggest_path) if f.lower().endswith((".wav", ".mp3"))]
    if not file_names:
        print("⚠️ Aucun fichier de suggestion trouvé.")
        return pink_noise

    # Liste de fichiers avec chemins complets (lecture à la demande)
    file_paths = [os.path.join(suggest_path, f) for f in file_names]

    total_samples = int(duree_totale * sample_rate)

    # Fenêtres REM nominales
    rem_windows = compute_rem_windows(duree_totale)
    if not rem_windows:
        print("ℹ️ Durée trop courte : aucune fenêtre REM couverte.")
        return pink_noise

    rng = np.random.default_rng()

    # Itère sur les fenêtres REM
    for w_idx, (rem_start_s, rem_end_s) in enumerate(rem_windows):
        # Fenêtre d’influence : rampe avant la REM + la REM elle-même
        # Bornée par start_delay_sec (aucune suggestion avant) et la durée totale.
        w_start_s = max(rem_start_s - REM_PRE_RAMP_S, start_delay_sec)
        w_end_s   = min(rem_end_s, duree_totale)
        if w_end_s <= w_start_s:
            continue

        win_len_s   = w_end_s - w_start_s
        occ_limit_s = win_len_s * SUGG_MAX_WINDOW_OCCUPANCY

        # Ordre randomisé des fichiers (on peut réutiliser si SUGG_REUSE_FILES=True)
        order = np.arange(len(file_paths))
        rng.shuffle(order)

        used_time_s = 0.0
        placed_intervals = []  # liste de (start_s, end_s) pour cette fenêtre

        # Tirage du temps dans la fenêtre (bias vers la fin pour la 1ʳᵉ fenêtre)
        def draw_time(start_s, end_s, voice_len_s, towards_end):
            # On garde une marge pour la durée de la voix
            lo = start_s
            hi = max(start_s, end_s - voice_len_s)
            if hi <= lo:
                return None
            u = rng.random()
            if towards_end:
                # Biais quadratique vers la fin (pousse les insertions vers la fin)
                u = u ** 2
            return lo + (hi - lo) * u

        passes = 0
        max_passes = 3 if SUGG_REUSE_FILES else 1

        while used_time_s < occ_limit_s and passes < max_passes:
            for idx in order:
                fpath = file_paths[idx]

                # ✅ Lecture universelle + rééchantillonnage auto à `sample_rate`
                voice_data, _sr = load_audio_any(fpath, sample_rate)
                if voice_data is None:
                    # MP3 non supporté par le build libsndfile → ignorer proprement
                    if fpath.lower().endswith(".mp3"):
                        print(f"⚠️ {os.path.basename(fpath)} ignoré (MP3 non supporté par votre libsndfile).")
                    continue

                voice_len_s = len(voice_data) / sample_rate

                # Limite d'occupation de la fenêtre
                if used_time_s + voice_len_s > occ_limit_s:
                    continue

                # 1ʳᵉ REM → accumulation progressive vers la fin ; sinon uniforme
                towards_end = (w_idx == 0)
                t_s = draw_time(w_start_s, w_end_s, voice_len_s, towards_end=towards_end)
                if t_s is None:
                    continue

                # Écart minimal entre suggestions (base + proportionnel à la durée de la voix)
                min_gap = SUGG_MIN_GAP_BASE_S + voice_len_s * SUGG_GAP_FACTOR
                ok = True
                for (a, b) in placed_intervals:
                    # Non-overlap avec marge (min_gap) de part et d’autre
                    if not (t_s - min_gap >= b or (t_s + voice_len_s) + min_gap <= a):
                        ok = False
                        break
                if not ok:
                    continue

                # Conversion en échantillons + bornes pour ducking
                insert = int(t_s * sample_rate)
                fade_samp = int(FADE_SEC * sample_rate)
                if insert < 0 or insert + len(voice_data) + fade_samp + 1 >= total_samples:
                    continue

                # Ducking + ajout de la voix
                pink_noise = apply_ducking(pink_noise, voice_data, insert, sample_rate)

                # Met à jour l’état de la fenêtre
                placed_intervals.append((t_s, t_s + voice_len_s))
                used_time_s += voice_len_s

                # Stop si on est très proche de la limite d'occupation
                if used_time_s >= occ_limit_s * 0.98:
                    break

            passes += 1

        if DEBUG:
            print(f"[REM {w_idx+1}] start={w_start_s:.0f}s end={w_end_s:.0f}s "
                  f"occupé≈{used_time_s:.1f}s (limite {occ_limit_s:.1f}s), "
                  f"suggestions={len(placed_intervals)}")

    return pink_noise



# ================================
# 🥁 Kick
# ================================

def synth_one_kick(sample_rate=SAMPLE_RATE, dur_sec=0.6,
                   f_start=KICK_F_START, f_end=KICK_F_END,
                   attack_sec=KICK_ATTACK_SEC, decay_sec=KICK_DECAY_SEC,
                   add_h2_db=KICK_H2_DB, drive=KICK_DRIVE):

    """
    Génère un unique coup de kick synthétique.
    Inspiré des kicks "Weightless-like" : doux, grave, arrondi.

    - sample_rate : fréquence d’échantillonnage (Hz)
    - dur_sec     : durée totale du kick (s)
    - f_start     : fréquence de départ de l'enveloppe de pitch (Hz)
    - f_end       : fréquence finale (Hz)
    - attack_sec  : durée de l’attaque (s) → montée progressive
    - decay_sec   : durée du relâchement (s)
    - add_h2_db   : niveau de la 2e harmonique (dB)
    - drive       : intensité de saturation douce (0 → neutre, 1 → forte)

    Retourne : tableau numpy.float32 normalisé (signal du kick).
    """

    n = int(dur_sec * sample_rate)
    t = np.arange(n) / sample_rate

    # Enveloppe de pitch (descente exponentielle douce)
    k = np.log(f_end / f_start) / max(1e-9, dur_sec)
    f_t = f_start * np.exp(k * t)
    phase = 2 * np.pi * np.cumsum(f_t) / sample_rate

    # Signal de base : sinus + 2e harmonique
    base  = np.sin(phase)
    harm2 = np.sin(2 * phase) * db_to_lin(add_h2_db)

    # Enveloppe d’amplitude (attaque + decay)
    env = np.ones_like(t)
    a_n = int(max(1, attack_sec * sample_rate))
    env[:a_n] = np.linspace(0.0, 1.0, a_n, endpoint=False)  # attaque
    env[a_n:] = np.linspace(1.0, 0.0, len(t) - a_n)         # decay

    # Application enveloppe + saturation
    x = (base + harm2) * env
    x = np.tanh(x * (1.0 + drive))          # saturation douce
    x = one_pole_hp(x, 20.0, sample_rate)   # coupe très graves (<20Hz)
    x = one_pole_lp(x, KICK_LPF_HZ, sample_rate)  # arrondit les aigus

    # Normalisation interne
    peak = np.max(np.abs(x)) + 1e-9
    x = x / peak

    # Atténuation globale du kick
    x *= db_to_lin(KICK_GAIN_DB)
    return x.astype(np.float32)


def build_kick_track(total_len_samples, sample_rate=SAMPLE_RATE):
    """
    Construit la piste complète de kick sur toute la durée.
    - Respecte la durée de section + décélération BPM + fade-out final.

    - total_len_samples : longueur totale du morceau (en échantillons)
    - sample_rate       : fréquence d’échantillonnage (Hz)

    Retourne : tableau numpy.float32 contenant les kicks placés.
    """

    # Durée de la section kick
    section_samples = int(min(KICK_SECTION_SEC, total_len_samples / sample_rate) * sample_rate)
    kick_track = np.zeros(total_len_samples, dtype=np.float32)

    # Génération d’un coup unique de kick
    one_kick = synth_one_kick(sample_rate=sample_rate)

    # Placement des coups selon BPM décroissant
    t_sec = 0.0
    end_sec = section_samples / sample_rate
    while t_sec < end_sec:
        # Interpolation BPM (décélération progressive)
        if t_sec < KICK_DECEL_SEC:
            p = t_sec / max(1e-9, KICK_DECEL_SEC)
            bpm = KICK_START_BPM + (KICK_END_BPM - KICK_START_BPM) * p
        else:
            bpm = KICK_END_BPM

        # Placement du coup
        period = 60.0 / bpm
        idx = int(t_sec * sample_rate)
        end_idx = min(idx + len(one_kick), total_len_samples)
        seg = one_kick[:end_idx - idx]
        kick_track[idx:end_idx] += seg

        t_sec += period

    # Fade-out sur la fin de la section
    fade_samples = int(min(KICK_FADEOUT_SEC, end_sec) * sample_rate)
    if fade_samples > 0:
        start = int(end_sec * sample_rate) - fade_samples
        start = max(0, start)
        fade = np.linspace(1.0, 0.0, fade_samples).astype(np.float32)
        kick_track[start:start+fade_samples] *= fade

    # Normalisation douce avec headroom
    peak = np.max(np.abs(kick_track))
    if peak > 0:
        kick_track = KICK_NORMAL * (kick_track / peak)

    return kick_track


# ================================
# 🎵 Génération bruit rose + mix
# ================================


def apply_ducking(pink_noise, voice, start_sample, sample_rate):

    """
    Applique un "ducking" : atténue le bruit rose pour laisser
    de la place à la voix insérée.
    - pink_noise   : signal de bruit rose
    - voice        : signal voix
    - start_sample : position d’insertion (échantillons)
    - sample_rate  : fréquence d’échantillonnage
    """

    fade_samples = int(FADE_SEC * sample_rate)
    end_sample = start_sample + len(voice)

    # Sécurité : éviter de dépasser la longueur du bruit rose
    if end_sample + fade_samples > len(pink_noise):
        end_sample = len(pink_noise) - fade_samples

    # Courbe de fondu autour de la voix
    fade_curve = smooth_fade_curve(fade_samples)
    sustain_gain = db_to_lin(DUCK_DB)   # atténuation du fond
    voice_gain   = db_to_lin(VOICE_DB)  # amplification de la voix

    # Atténuation progressive avant la voix
    pink_noise[start_sample:start_sample+fade_samples] *= (
        fade_curve * (1 - sustain_gain) + sustain_gain
    )
    # Atténuation constante pendant la voix
    pink_noise[start_sample+fade_samples:end_sample] *= sustain_gain
    # Retour progressif après la voix
    pink_noise[end_sample:end_sample+fade_samples] *= (
        fade_curve[::-1] * (1 - sustain_gain) + sustain_gain
    )

    # Ajout de la voix
    pink_noise[start_sample:end_sample] += voice * voice_gain
    return pink_noise


def build_pink_waves_envelope(total_len_samples, sr):

    """
    Envelope 1D pour moduler le bruit rose en vagues sur la fenêtre définie.
    """

    window_samples = int(min(PINK_WAVES_WINDOW_SEC, total_len_samples / sr) * sr)
    if window_samples <= 0:
        return np.ones(total_len_samples, dtype=np.float32)

    upN   = max(1, int(PINK_WAVE_UP_SEC   * sr))
    holdN = max(1, int(PINK_WAVE_HOLD_SEC * sr))
    downN = max(1, int(PINK_WAVE_DOWN_SEC * sr))

    # courbes douces: montée = fade inversé, descente = fade standard
    up   = smooth_fade_curve(upN)[::-1]                  # 0 -> 1
    hold = np.ones(holdN, dtype=np.float32)              # 1
    down = smooth_fade_curve(downN)                      # 1 -> 0

    cycle = np.concatenate([up, hold, down]).astype(np.float32)

    # Mise à l'échelle entre MIN et MAX
    amp_min, amp_max = PINK_WAVE_MIN_AMP, PINK_WAVE_MAX_AMP
    cycle = amp_min + (amp_max - amp_min) * cycle

    # Répéter le cycle pour couvrir la fenêtre
    reps = window_samples // len(cycle) + 1
    env_section = np.tile(cycle, reps)[:window_samples]

    # Enveloppe globale = env_section (fenêtre 30 min), puis 1.0
    env = np.ones(total_len_samples, dtype=np.float32)
    env[:window_samples] = env_section
    return env




# ================================
# 🚀 Script principal
# ================================



def main_generate(duree_totale, fade_out, save_path, kick_enabled=True, waves_enabled=True):
    """
    Génère la piste audio complète (bruit rose + vagues + kick + voix).

    Étapes :
    1. Génération bruit blanc → filtrage en bruit rose
    2. Application éventuelle de modulation en vagues (respiration)
    3. Génération piste de kick + mélange
    4. Application du fade-out (fin progressive)
    5. Insertion des suggestions vocales avec ducking
    6. Normalisation du mix final
    7. Écriture fichiers intermédiaires (debug) + fichier final

    - duree_totale  : durée totale du rendu (s)
    - fade_out      : durée du fondu de sortie (s)
    - save_path     : chemin du fichier final .wav
    - kick_enabled  : active/désactive la piste kick
    - waves_enabled : active/désactive l’effet de vagues
    """

    sample_rate = 44100
    samples = duree_totale * sample_rate

    # 1. Génération bruit blanc → filtrage en bruit rose
    white = np.random.normal(0, 1, samples).astype(np.float32)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    pink = lfilter(b, a, white).astype(np.float32)
    pink /= (np.max(np.abs(pink)) + 1e-9)

    # 2. Modulation en vagues (si activée)
    if waves_enabled:
        env = build_pink_waves_envelope(len(pink), sample_rate)
        pink *= env
    log_stage("pink", pink)

    # 3. Génération kick + mélange (si activé)
    if kick_enabled:
        kick = build_kick_track(len(pink), sample_rate)
        log_stage("kick", kick)
        mix = pink + kick
    else:
        kick = np.zeros_like(pink)  # placeholder vide pour debug
        mix = pink
    log_stage("mix_before_suggest", mix)

    # 4. Fade-out final (optionnel)
    if fade_out > 0:
        fN = fade_out * sample_rate
        fade = np.linspace(1, 0, fN, dtype=np.float32)
        mix[-fN:] *= fade
        log_stage("mix_after_fade", mix)

    # 5. Intégration des suggestions vocales
    mix = integrate_suggestions(mix, sample_rate, duree_totale,
                                start_delay_sec=SUGGEST_DELAY_SEC)
    log_stage("mix_after_suggest", mix)

    # 6. Normalisation finale (headroom ~2%)
    peak = np.max(np.abs(mix))
    if peak > 1e-9:
        mix = 0.98 * (mix / peak)
    log_stage("final", mix)

    # 7. Sauvegarde fichiers (intermédiaires + final)
    temp_dir = ensure_temp_dir()
    try:
        # Fichiers intermédiaires (debug uniquement)
        safe_write_wav(os.path.join(temp_dir, "_pink.wav"), pink, sample_rate, verbose=False)
        safe_write_wav(os.path.join(temp_dir, "_kick.wav"), kick, sample_rate, verbose=False)
        safe_write_wav(os.path.join(temp_dir, "_mix_before_suggest.wav"), mix, sample_rate, verbose=False)

        # Fichier final (avec log visible)
        safe_write_wav(save_path, mix.astype(np.float32), sample_rate)

    finally:
        # Nettoyage du contenu de TEMP_DIR
        clear_temp_dir()
        


if __name__ == "__main__":

    """
    Point d’entrée du script :
    1. Vérifie la présence des dépendances
    2. Gère la création d’un venv ou installation globale
    3. Récupère durée totale, fade-out + options kick/vagues
    4. Lance l’UI pour choisir le chemin de sauvegarde
    5. Génère le mix final (bruit rose + kick + options)
    """

    # 1. Vérification des dépendances
    print("🔍 Vérification des dépendances…")
    if "--skip-setup" not in sys.argv:
        missing_libs = check_libs()
        if missing_libs:
            print(f"⚠️ Librairies manquantes: {', '.join(missing_libs)}")
            choix = input("Créer un environnement virtuel (V) ou installer globalement (G) ? [V/G] : ").strip().lower()
            if choix == "v":
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
            print("✅ Toutes les librairies sont déjà installées.\n")

    # 2. Lecture des paramètres (CLI ou input)
    kick_enabled = True   # valeur par défaut
    waves_enabled = True  # valeur par défaut

    if len(sys.argv) >= 3:
        try:
            duree_totale = int(sys.argv[1])
            fade_out = int(sys.argv[2])

            # si on a aussi kick et vagues
            if len(sys.argv) >= 5:
                kick_enabled = bool(int(sys.argv[3]))
                waves_enabled = bool(int(sys.argv[4]))

            if duree_totale <= 0 or fade_out < 0 or fade_out >= duree_totale:
                raise ValueError
        except ValueError:
            duree_totale = ask_positive_int("Durée totale en secondes : ")
            fade_out = ask_positive_int("Fade-out en secondes : ", max_val=duree_totale)
    else:
        duree_totale = ask_positive_int("Durée totale en secondes : ")
        fade_out = ask_positive_int("Fade-out en secondes : ", max_val=duree_totale)

    # 3. Spinner (feedback visuel)
    spinner = Spinner()
    spinner.loading_start("Génération du mix (bruit rose + kick + options)")

    # 4. UI sauvegarde fichier
    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("Fichiers WAV", "*.wav")],
        title="Enregistrer l'audio",
        initialfile="sleepy_pinknoise.wav"
    )

    # 5. Génération ou annulation
    if save_path:
        try:
            # ⚡️ On passe maintenant kick_enabled et waves_enabled
            main_generate(duree_totale, fade_out, save_path, kick_enabled, waves_enabled)
            spinner.loading_stop("Son généré")
            print(f"Chemin du fichier : {os.path.abspath(save_path)}")
        except Exception as e:
            spinner.loading_stop("Erreur pendant la génération")
            print("❌ Exception:", e)
            traceback.print_exc()
        finally:
            time.sleep(1)
            sys.exit()
    else:
        spinner.loading_stop("Enregistrement annulé")
        time.sleep(1)
        sys.exit()



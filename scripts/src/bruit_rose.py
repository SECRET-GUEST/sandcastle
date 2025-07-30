import subprocess, sys, time, os, importlib
import tkinter as tk
from tkinter import filedialog
from loadingSpinner import Spinner
import numpy as np
import soundfile as sf
from scipy.signal import lfilter

# ================================
# 🔧 Librairies requises
# ================================
REQUIRED_LIBS = ["numpy", "scipy", "soundfile"]

# ================================
# 📦 Gestion des dépendances
# ================================
def install_libs(env_path=None):
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    if env_path:
        pip_cmd = [os.path.join(env_path, "Scripts", "python"), "-m", "pip", "install", "-r", "requirements.txt"]
    subprocess.check_call(pip_cmd)

def create_venv():
    env_path = os.path.join(os.getcwd(), "env_sandcastle")
    subprocess.check_call([sys.executable, "-m", "venv", env_path])
    return env_path

def check_libs():
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



# ================================
# 🎛 Traitement audio
# ================================

DUCK_DB = -3       # Atténuation douce pendant la voix
FADE_SEC = 5       # Fondu de 5 sec avant/après
VOICE_DB = 6       # Gain ajouté à la voix pour plus de clarté

import numpy as np

def smooth_fade_curve(length):
    """Génère une courbe cos² douce pour le fondu"""
    t = np.linspace(0, np.pi / 2, length)
    return np.cos(t)**2  # décroissance douce

def normalize_audio(data):
    """Normalise un signal audio (peu importe mono/stéréo)"""
    max_val = np.max(np.abs(data))
    return data / max_val if max_val > 0 else data

def ensure_mono(data):
    """Convertit en mono si l'audio est stéréo"""
    if data.ndim > 1:  # Plus d'un canal
        data = data.mean(axis=1)
    return data

def apply_ducking(pink_noise, voice, start_sample, sample_rate):
    """Applique un ducking ultra doux sans oscillation"""
    fade_samples = int(FADE_SEC * sample_rate)
    end_sample = start_sample + len(voice)

    # Sécurité : bornes
    if end_sample + fade_samples > len(pink_noise):
        end_sample = len(pink_noise) - fade_samples

    # Courbes douces
    fade_curve = smooth_fade_curve(fade_samples)
    sustain_gain = 10**(DUCK_DB / 20)  # Atténuation constante
    voice_gain = 10**(VOICE_DB / 20)

    # 🔹 1. Fade out
    pink_noise[start_sample:start_sample+fade_samples] *= (
        fade_curve * (1 - sustain_gain) + sustain_gain
    )

    # 🔹 2. Partie centrale atténuée
    pink_noise[start_sample+fade_samples:end_sample] *= sustain_gain

    # 🔹 3. Fade in
    pink_noise[end_sample:end_sample+fade_samples] *= (
        fade_curve[::-1] * (1 - sustain_gain) + sustain_gain
    )

    # 🔹 4. Ajouter voix
    pink_noise[start_sample:end_sample] += voice * voice_gain

    return pink_noise



def integrate_suggestions(pink_noise, sample_rate, duree_totale):
    """Ajoute suggestions vocales espacées intelligemment"""
    suggest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
    files = [f for f in os.listdir(suggest_path) if f.endswith(".wav")]

    if not files:
        print("⚠️ Aucun fichier de suggestion trouvé.")
        return pink_noise

    total_samples = duree_totale * sample_rate
    interval = total_samples // (len(files) + 1)  # Espacement égal

    for i, filename in enumerate(files):
        voice_path = os.path.join(suggest_path, filename)
        voice_data, sr = sf.read(voice_path)

        # Vérification sample rate
        if sr != sample_rate:
            print(f"⚠️ {filename} ignoré (mauvais sample rate).")
            continue

        # Préparer la voix
        voice_data = ensure_mono(voice_data)
        voice_data = normalize_audio(voice_data)

        # Calcul de la position d’insertion
        start_sample = (i + 1) * interval
        pink_noise = apply_ducking(pink_noise, voice_data, start_sample, sample_rate)

    return pink_noise



# ================================
# 🎵 Génération bruit rose
# ================================
def main_generate(duree_totale, fade_out, save_path):
    sample_rate = 44100
    samples = duree_totale * sample_rate

    # Génération bruit blanc
    white_noise = np.random.normal(0, 1, samples).astype(np.float32)

    # Filtrage -> bruit rose
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    pink_noise = lfilter(b, a, white_noise)
    pink_noise /= np.max(np.abs(pink_noise))

    # Fade-out global si défini
    if fade_out > 0:
        fade_samples = fade_out * sample_rate
        fade_curve = np.linspace(1, 0, fade_samples)
        pink_noise[-fade_samples:] *= fade_curve

    # Ajout suggestions
    pink_noise = integrate_suggestions(pink_noise, sample_rate, duree_totale)

    # Sauvegarde
    if save_path:
        sf.write(save_path, pink_noise, sample_rate)

# ================================
# 🚀 Script principal
# ================================
if __name__ == "__main__":
    print("🔍 Vérification des dépendances...")

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

    if len(sys.argv) >= 3:
        try:
            duree_totale = int(sys.argv[1])
            fade_out = int(sys.argv[2])
            if duree_totale <= 0 or fade_out < 0 or fade_out >= duree_totale:
                raise ValueError
        except ValueError:
            duree_totale = ask_positive_int("Durée totale en secondes : ")
            fade_out = ask_positive_int("Fade-out en secondes : ", max_val=duree_totale)
    else:
        duree_totale = ask_positive_int("Durée totale en secondes : ")
        fade_out = ask_positive_int("Fade-out en secondes : ", max_val=duree_totale)

    spinner = Spinner()
    spinner.loading_start("Génération du bruit rose")

    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Fichiers WAV", "*.wav")], title="Enregistrer le bruit rose", initialfile="bruit_rose_filtré.wav")

    if save_path:
        main_generate(duree_totale, fade_out, save_path)
        spinner.loading_stop("Son généré")
        print(f"Chemin du fichier : {save_path}\n")
        time.sleep(1)
        sys.exit()
    else:
        spinner.loading_stop("Enregistrement annulé")
        time.sleep(1)
        sys.exit()

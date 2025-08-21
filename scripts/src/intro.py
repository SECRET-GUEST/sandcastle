import sys, time, os, threading, msvcrt, winsound

skip_intro = False
CLS = 'cls' if os.name == 'nt' else 'clear'

# === Détection touche skip intro ===
def check_skip():
    """Permet à l’utilisateur de passer l’intro en appuyant sur une touche"""
    global skip_intro
    start_time = time.time()
    while time.time() - start_time < 2:
        if msvcrt.kbhit():
            msvcrt.getch()
            skip_intro = True
            break

# === Typewriter ===
def typewriter(text, delay=0.02, newline=True):
    """Affiche un texte caractère par caractère, saute si intro passée"""
    global skip_intro
    if skip_intro:
        print(text)
        return text
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return text

# === Typewriter avec input sur la même ligne ===
def typed_input(prompt, delay=0.02):
    """Affiche un texte caractère par caractère et récupère une saisie sur la même ligne"""
    global skip_intro
    if skip_intro:
        return input(prompt)
    for char in prompt:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    return input(" ")

# === Animation ASCII SandCastle ===
ascii_art = [
"   _____              _   _   _____       _____               _____   _______   _        ______ ",
"  / ____|     /\\     | \\ | | |  __ \\     / ____|     /\\      / ____| |__   __| | |      |  ____|",
" | (___      /  \\    |  \\| | | |  | |   | |         /  \\    | (___      | |    | |      | |__   ",
"  \\___ \\    / /\\ \\   | . ` | | |  | |   | |        / /\\ \\    \\___ \\     | |    | |      |  __|  ",
"  ____) |  / ____ \\  | |\\  | | |__| |   | |____   / ____ \\   ____) |    | |    | |____  | |____ "
]

frames = [
    ([4], []),
    ([3, 5], [2, 3]),
    ([2, 6], [1, 2, 3, 4]),
    ([1, 7], list(range(5)))
]

def draw_frame(eq_lines, unlocked_lines):
    """Construit le cadre ASCII pour la frame en cours"""
    frame = []
    for i in range(1, 8):
        if i in eq_lines:
            frame.append("=" * 96)
        elif 1 < i < 7 and (i - 2) in unlocked_lines:
            frame.append(ascii_art[i - 2])
        else:
            frame.append(" " * 96)
    return "\n".join(frame)

def animate_frames():
    """Joue le son d’ouverture + anime SandCastle"""
    
    # Lancement son opening.wav en async
    sound_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/SE/opening.wav"))
    if os.path.exists(sound_path):
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    os.system(CLS)
    print("\n" * 3 + "=" * 96 + "\n" * 3)
    time.sleep(0.3)
    for eq, unlocked in frames:
        os.system(CLS)
        print(draw_frame(eq, unlocked))
        time.sleep(0.3)
    os.system(CLS)
    print(draw_frame([1, 7], list(range(5))))
    time.sleep(0.5)
    

# === Main ===
def main():
    os.system(CLS)

    # Lancement du thread pour détecter si l’utilisateur veut passer l’intro
    thread = threading.Thread(target=check_skip)
    thread.start()

    # Compte à rebours skip intro
    for i in range(2, -1, -1):
        sys.stdout.write(f"\rAppuyez sur une touche pour passer l'intro ({i})   ")
        sys.stdout.flush()
        time.sleep(1)
        if skip_intro:
            break
    thread.join()
    os.system(CLS)

    # Animation SandCastle
    animate_frames()
    # === Infos essentielles sur le sommeil et le bruit rose ===
    typewriter("\nINFORMATION ESSENTIELLE :", delay=0.005)
    typewriter("Le bruit rose est scientifiquement reconnu pour améliorer la qualité du sommeil profond.", delay=0.02)
    typewriter("Source : Ngo, Hong-Viet V., et al. « Enhancing Slow Wave Sleep with Auditory Stimulation. » Frontiers in Human Neuroscience, 2017.", delay=0.005)
    print()
    typewriter("Le sommeil se déroule en cycles d’environ 90 minutes :", delay=0.02)
    print()
    typewriter("- Sommeil léger (transition vers l’endormissement).", delay=0.02)
    typewriter("- Sommeil profond (récupération physique et réparation du corps).", delay=0.02)
    typewriter("- Sommeil paradoxal (REM) : phase des rêves et de la créativité.", delay=0.02)
    print()
    print()
    
    # === Comprendre les cycles REM et placement des suggestions ===
    typewriter("Les phases REM, où la majorité des rêves surviennent, apparaissent :", delay=0.02)
    typewriter("- Fin du 1er cycle : environ 75 à 90 minutes après endormissement (~4500 secondes).", delay=0.02)
    typewriter("- Fin du 2e cycle : environ 165 à 180 minutes (~10800 secondes).", delay=0.02)
    typewriter("- Fin du 3e cycle : environ 255 à 270 minutes (~16200 secondes).", delay=0.02)
    typewriter("Les suggestions audio doivent être placées juste avant ou pendant ces fenêtres.", delay=0.02)
    print()
    print()

    # === Astuce + avertissement combinés ===
    typewriter("ASTUCE & PRÉCAUTION :", delay=0.005)
    typewriter("Utiliser un fade-out progressif (~30 minutes) réduit le risque de réveil brutal à la fin d’un cycle REM.", delay=0.02)
    print()
    typewriter("Sans fade-out : le sommeil profond est réduit, la phase REM est renforcée, ce qui peut augmenter la créativité mais aussi la fatigue.", delay=0.02)
    print()
    typewriter("Cette technique était utilisée par Salvador Dalí pour stimuler sa créativité grâce à des micro-sommeils interrompus.", delay=0.02)
    typewriter("Source : Salvador Dalí, 50 Secrets of Magic Craftsmanship (1948) et sa « technique de la clé ».", delay=0.005)
    print()
    typewriter("⚠️ À n’utiliser qu’occasionnellement pour éviter une fatigue chronique.", delay=0.02)
    print()
    print()

    # === Oniromancie ===
    typewriter("ONIROMANCIE :", delay=0.005)
    typewriter("L’oniromancie est l’art d’orienter ses rêves à l’aide de suggestions audio ciblées.", delay=0.02)
    typewriter("Ce processus repose sur la psychologie et les cycles REM (pas de magie).", delay=0.02)
    typewriter("Les suggestions audio doivent être diffusées durant les moments REM identifiés.", delay=0.02)
    typewriter("Votre propre voix est plus efficace car le cerveau la reconnaît comme une pensée interne, réduisant la résistance aux suggestions.", delay=0.02)
    print()
    typewriter("Source : *Journal of Cognitive Neuroscience*, étude sur la perception des voix internes, 2015.", delay=0.005)
    print()


    # === Choix création suggestions audio ===
    typewriter("Souhaitez-vous créer des suggestions audio pour orienter vos rêves ? (o/n)\n", delay=0.02)
    choix = ""
    while choix not in ("o", "n"):
        choix = input("> ").strip().lower()

    if choix == "o":
        typewriter("\nTrès bien.", delay=0.02)
        typewriter("Pour cela, vous pouvez utiliser un logiciel gratuit comme Audacity.", delay=0.02)
        typewriter("Enregistrez des phrases simples, affirmatives, et positives.", delay=0.02)
        typewriter("Quelques exemples :", delay=0.02)
        print()
        typewriter('- "Je me déplace dans un lieu calme et lumineux."', delay=0.02)
        typewriter('- "Je visite un endroit magnifique et apaisant."', delay=0.02)
        typewriter('- "Je retiens mes rêves au réveil."', delay=0.02)
        print()
        typewriter("\nEnregistrez vos fichiers au format WAV.", delay=0.02)
        typewriter("Placez-les dans le dossier : scripts/Assets/SFX/Suggests", delay=0.02)
        typewriter("Ils seront utilisés automatiquement par le programme.", delay=0.02)

        # Ouvre automatiquement le dossier de suggestions
        se_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
        os.startfile(se_path)

    # === Saisie durées bruit rose ===
    duree = typed_input("\nEntrez la durée totale en secondes (ex: 7200 pour 2h) : ")
    print()
    fade = typed_input("\nEntrez la durée du fade-out en secondes (ex: 1800 pour 30 min) : ")

    # === Lancement script bruit_rose ===
    print("\nLancement du script de bruit rose...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    bruit_rose_path = os.path.join(script_dir, "bruit_rose.py")
    os.system(f'python "{bruit_rose_path}" {duree} {fade}')
    
    # Stop le son une fois l’animation terminée
    winsound.PlaySound(None, winsound.SND_PURGE)

if __name__ == "__main__":
    main()

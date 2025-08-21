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
    print()
    typewriter("Le bruit rose est scientifiquement reconnu pour améliorer la qualité du sommeil profond.", delay=0.02)
    print()
    typewriter("Source : Ngo, Hong-Viet V., et al. « Enhancing Slow Wave Sleep with Auditory Stimulation. » Frontiers in Human Neuroscience, 2017.", delay=0.005)
    print()

    # === Oniromancie ===
    typewriter("SUGGESTIONS AUDIO :", delay=0.005)
    print()
    typewriter("Le sommeil alterne des cycles d’environ 90 minutes (léger → profond → paradoxal ; phase REM).", delay=0.02)
    typewriter("La majorité des rêves vifs surviennent en phase REM.", delay=0.02)
    print()
    typewriter("Sandcastle peut diffuser vos phrases simples et positives juste avant / pendant chaque fenêtre REM couverte par votre durée :", delay=0.02)
    typewriter("- 1ere REM : ~75–90 min après l’endormissement (≈ 4500 s).", delay=0.02)
    typewriter("- 2e REM  : ~165–180 min (≈ 10800 s).", delay=0.02)
    typewriter("- 3e REM  : ~255–270 min (≈ 16200 s).", delay=0.02)
    print()
    typewriter("si l'audio est assez long, des suggestions seront placées avant chaque fenêtre listée.", delay=0.02)
    typewriter("Astuce : utilisez votre propre voix (mots simples, positifs). Le cerveau la perçoit comme une pensée interne, ce qui peut faciliter l’intégration.", delay=0.02)
    print()
    typewriter("Source : Journal of Cognitive Neuroscience, étude sur la perception des voix internes, 2015.", delay=0.005)
    print()
    print()

    # === Comprendre les cycles REM et placement des suggestions ===

    print()
    print()

    # === Explication vagues ===
    typewriter("RESPIRATION GUIDÉE :", delay=0.005)
    print()
    typewriter("Les vagues de bruit rose simulent une respiration lente (4-2-6).", delay=0.02)
    typewriter("Si vous décidez de les activer, inspirez 4 sec → retenez 2 sec → expirez 6 sec, calés sur les vagues.", delay=0.02)
    print()
    typewriter("Cette méthode est inspirée des techniques militaires d’endormissement rapide.", delay=0.02)
    print()
    typewriter("Source : U.S. Army Field Manual FM 22-51, Sleep Management in Combat, 1983.", delay=0.005)
    print()
    print()

    # === Explication kick ===
    typewriter("RYTHME CARDIAQUE :", delay=0.005)
    print()
    typewriter("Le kick basse fréquence agit comme un métronome cardiaque.", delay=0.02)
    typewriter("Votre cœur tend naturellement à se synchroniser à un rythme sonore régulier", delay=0.02)
    print()
    typewriter("⚠️ Remarque : le kick est calé à ~60 BPM (rythme naturel du repos).", delay=0.02)
    typewriter("Pour la majorité des personnes cela favorise l’apaisement, mais si vous avez un trouble cardiaque ou ressentez une gene, désactivez cette option.", delay=0.02)
    print()
    typewriter("Source : Bernardi, L. et al. « Cardiovascular, cerebrovascular, and respiratory changes induced by different types of music. » Circulation, 2009.", delay=0.005)
    print()
    print()

    # === Astuce + avertissement combinés ===
    typewriter("ASTUCE & PRÉCAUTION :", delay=0.005)
    typewriter("Utiliser un fade-out progressif (~30 minutes) réduit le risque de réveil brutal à la fin d’un cycle REM.", delay=0.02)
    print()
    typewriter("Sans fade-out : le sommeil profond est réduit, la phase REM est renforcée, ce qui peut augmenter la créativité mais aussi la fatigue.", delay=0.02)
    typewriter("Cette technique était utilisée par Salvador Dalí pour stimuler sa créativité grâce à des micro-sommeils interrompus.", delay=0.02)
    typewriter("⚠️ À n’utiliser qu’occasionnellement pour éviter une fatigue chronique.", delay=0.02)
    print()
    typewriter("Source : Salvador Dalí, 50 Secrets of Magic Craftsmanship (1948) et sa « technique de la clé ».", delay=0.005)
    print()
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

        se_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
        os.startfile(se_path)

    # === Saisie durées bruit rose ===
    while True:
        try:
            duree = int(typed_input("\nEntrez la durée totale en secondes (minimum 7200 = 2h) : "))
            if duree < 7200:
                print("❌ Durée trop courte. Minimum requis : 7200 secondes (2h).")
                continue
            break
        except ValueError:
            print("❌ Veuillez entrer un nombre valide.")

    while True:
        try:
            fade = int(typed_input("Entrez la durée du fade-out en secondes (0 = désactivé, recommandé ≥ 1800 = 30 min) : "))
            if fade >= duree:
                print("❌ Le fade-out doit être inférieur à la durée totale.")
                continue
            if fade == 0:
                print("⚠️ Aucun fade-out : risque de réveil brutal.")
            elif fade < 1800:
                print("⚠️ Attention : un fade-out plus court que 30 minutes peut provoquer des réveils plus brusques.")
            break
        except ValueError:
            print("❌ Veuillez entrer un nombre valide.")

    # === Nouveaux choix kick & vagues ===
    kick_choice = typed_input("\nActiver le kick (rythme cardiaque) ? (O/n) : ").strip().lower()
    waves_choice = typed_input("Activer les vagues (respiration guidée) ? (O/n) : ").strip().lower()
    kick_enabled = (kick_choice != "n")
    waves_enabled = (waves_choice != "n")

    # === Lancement script bruit_rose avec options ===
    print("\n Création du chateau de sable ...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    bruit_rose_path = os.path.join(script_dir, "bruit_rose.py")
    os.system(f'python "{bruit_rose_path}" {duree} {fade} {int(kick_enabled)} {int(waves_enabled)}')
    
    # Stop le son une fois l’animation terminée
    winsound.PlaySound(None, winsound.SND_PURGE)

if __name__ == "__main__":
    main()

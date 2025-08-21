# OPENING | https://www.youtube.com/watch?v=_85LaeTCtV8

import sys, time, os, threading, msvcrt, winsound

skip_intro = False
CLS = 'cls' if os.name == 'nt' else 'clear'

# === Skip intro key detection ===
def check_skip():
    """Allows the user to skip the intro by pressing any key"""
    global skip_intro
    start_time = time.time()
    while time.time() - start_time < 2:
        if msvcrt.kbhit():
            msvcrt.getch()
            skip_intro = True
            break

# === Typewriter effect ===
def typewriter(text, delay=0.02, newline=True):
    """Prints text character by character, unless intro is skipped"""
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

# === Typewriter with input on the same line ===
def typed_input(prompt, delay=0.02):
    """Displays text with typewriter effect and gets input on the same line"""
    global skip_intro
    if skip_intro:
        return input(prompt)
    for char in prompt:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    return input(" ")

# === ASCII SandCastle Animation ===
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
    """Builds ASCII frame for the animation"""
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
    """Plays intro sound + SandCastle animation"""
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

    # Start thread to detect skip intro
    thread = threading.Thread(target=check_skip)
    thread.start()

    # Countdown for skip intro
    for i in range(2, -1, -1):
        sys.stdout.write(f"\rPress any key to skip intro ({i})   ")
        sys.stdout.flush()
        time.sleep(1)
        if skip_intro:
            break
    thread.join()
    os.system(CLS)

    # Animation SandCastle
    animate_frames()

    # === Essential info on sleep & pink noise ===
    typewriter("\nESSENTIAL INFORMATION:", delay=0.005)
    print()
    typewriter("Pink noise is scientifically recognized for improving deep sleep quality.", delay=0.02)
    print()
    typewriter("Source: Ngo, Hong-Viet V., et al. 'Enhancing Slow Wave Sleep with Auditory Stimulation.' Frontiers in Human Neuroscience, 2017.", delay=0.005)
    print()

    # === Audio suggestions ===
    typewriter("AUDIO SUGGESTIONS:", delay=0.005)
    print()
    typewriter("Sleep alternates in cycles of about 90 minutes (light → deep → REM).", delay=0.02)
    typewriter("Most vivid dreams occur during REM sleep.", delay=0.02)
    print()
    typewriter("SandCastle can play your simple, positive phrases right before / during each REM window covered by your duration:", delay=0.02)
    typewriter("- 1st REM: ~75–90 min after falling asleep (≈ 4500 s).", delay=0.02)
    typewriter("- 2nd REM: ~165–180 min (≈ 10800 s).", delay=0.02)
    typewriter("- 3rd REM: ~255–270 min (≈ 16200 s).", delay=0.02)
    print()
    typewriter("If the audio is long enough, suggestions will be placed before each listed window.", delay=0.02)
    typewriter("Tip: use your own voice (simple, positive words). The brain perceives it as an internal thought, which may help integration.", delay=0.02)
    print()
    typewriter("Source: Journal of Cognitive Neuroscience, 2015 study on inner voice perception.", delay=0.005)
    print()
    print()

    # === Guided breathing ===
    typewriter("GUIDED BREATHING:", delay=0.005)
    print()
    typewriter("Pink noise waves simulate slow breathing (4-2-6).", delay=0.02)
    typewriter("If enabled: inhale 4 sec → hold 2 sec → exhale 6 sec, in sync with the waves.", delay=0.02)
    print()
    typewriter("This method is inspired by military rapid sleep-induction techniques.", delay=0.02)
    print()
    typewriter("Source: U.S. Army Field Manual FM 22-51, Sleep Management in Combat, 1983.", delay=0.005)
    print()
    print()

    # === Heartbeat rhythm ===
    typewriter("HEART RATE:", delay=0.005)
    print()
    typewriter("The low-frequency kick acts like a heart metronome.", delay=0.02)
    typewriter("Your heart tends to naturally synchronize with a steady beat.", delay=0.02)
    print()
    typewriter("⚠️ Note: The kick is set to ~60 BPM (natural resting rhythm).", delay=0.02)
    typewriter("For most people this is calming, but if you have a heart condition or feel discomfort, disable this option.", delay=0.02)
    print()
    typewriter("Source: Bernardi, L. et al. 'Cardiovascular, cerebrovascular, and respiratory changes induced by different types of music.' Circulation, 2009.", delay=0.005)
    print()
    print()

    # === Tip & precaution ===
    typewriter("TIP & PRECAUTION:", delay=0.005)
    typewriter("Using a progressive fade-out (~30 minutes) reduces the risk of abrupt waking at the end of a REM cycle.", delay=0.02)
    print()
    typewriter("Without fade-out: deep sleep is reduced, REM phase is reinforced, boosting creativity but also fatigue.", delay=0.02)
    typewriter("This technique was used by Salvador Dalí to stimulate creativity through interrupted micro-naps.", delay=0.02)
    typewriter("⚠️ Only use occasionally to avoid chronic fatigue.", delay=0.02)
    print()
    typewriter("Source: Salvador Dalí, 50 Secrets of Magic Craftsmanship (1948) and his 'key technique'.", delay=0.005)
    print()
    print()

    # === Audio suggestions creation ===
    typewriter("Would you like to create audio suggestions to guide your dreams? (y/n)\n", delay=0.02)
    choice = ""
    while choice not in ("y", "n"):
        choice = input("> ").strip().lower()

    if choice == "y":
        typewriter("\nAlright.", delay=0.02)
        typewriter("You can use a free tool like Audacity.", delay=0.02)
        typewriter("Record short, affirmative, and positive sentences.", delay=0.02)
        typewriter("Examples:", delay=0.02)
        print()
        typewriter('- "I am walking in a calm and bright place."', delay=0.02)
        typewriter('- "I visit a beautiful, soothing environment."', delay=0.02)
        typewriter('- "I remember my dreams upon waking."', delay=0.02)
        print()
        typewriter("\nSave your files as WAV format.", delay=0.02)
        typewriter("Place them in: scripts/Assets/SFX/Suggests", delay=0.02)
        typewriter("They will be automatically used by the program.", delay=0.02)

        se_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
        os.startfile(se_path)

    # === Duration inputs ===
    while True:
        try:
            duration = int(typed_input("\nEnter total duration in seconds (minimum 7200 = 2h): "))
            if duration < 7200:
                print("❌ Too short. Minimum required: 7200 seconds (2h).")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number.")

    while True:
        try:
            fade = int(typed_input("Enter fade-out duration in seconds (0 = disabled, recommended ≥ 1800 = 30 min): "))
            if fade >= duration:
                print("❌ Fade-out must be shorter than total duration.")
                continue
            if fade == 0:
                print("⚠️ No fade-out: risk of abrupt wake-up.")
            elif fade < 1800:
                print("⚠️ Warning: fade-out shorter than 30 minutes may cause more abrupt waking.")
            break
        except ValueError:
            print("❌ Please enter a valid number.")

    # === Kick & waves choices ===
    kick_choice = typed_input("\nEnable kick (heartbeat rhythm)? (Y/n): ").strip().lower()
    waves_choice = typed_input("Enable waves (guided breathing)? (Y/n): ").strip().lower()
    kick_enabled = (kick_choice != "n")
    waves_enabled = (waves_choice != "n")

    # === Launch pink noise script with options ===
    print("\n Building the SandCastle ...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    bruit_rose_path = os.path.join(script_dir, "bruit_rose.py")
    os.system(f'python "{bruit_rose_path}" {duration} {fade} {int(kick_enabled)} {int(waves_enabled)}')
    
    # Stop sound once animation is done
    winsound.PlaySound(None, winsound.SND_PURGE)

if __name__ == "__main__":
    main()


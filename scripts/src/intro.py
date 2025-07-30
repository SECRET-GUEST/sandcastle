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

# === Typewriter ===
def typewriter(text, delay=0.02, newline=True):
    """Displays text character by character; skips if intro was bypassed"""
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
    """Displays text character by character and takes user input on the same line"""
    global skip_intro
    if skip_intro:
        return input(prompt)
    for char in prompt:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    return input(" ")

# === ASCII Animation SandCastle ===
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
    """Builds the ASCII frame for the current step"""
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
    """Plays opening sound + animates SandCastle"""
    
    # Play opening.wav sound asynchronously
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

    # Launch thread to detect if user wants to skip intro
    thread = threading.Thread(target=check_skip)
    thread.start()

    # Skip intro countdown
    for i in range(2, -1, -1):
        sys.stdout.write(f"\rPress any key to skip intro ({i})   ")
        sys.stdout.flush()
        time.sleep(1)
        if skip_intro:
            break
    thread.join()
    os.system(CLS)

    # SandCastle Animation
    animate_frames()
    
    # === Essential information on sleep and pink noise ===
    typewriter("\nESSENTIAL INFORMATION:", delay=0.005)
    typewriter("Pink noise is scientifically proven to improve deep sleep quality.", delay=0.02)
    typewriter("Source: Ngo, Hong-Viet V., et al. “Enhancing Slow Wave Sleep with Auditory Stimulation.” Frontiers in Human Neuroscience, 2017.", delay=0.005)
    print()
    typewriter("Sleep occurs in cycles of about 90 minutes:", delay=0.02)
    print()
    typewriter("- Light sleep (transition into sleep).", delay=0.02)
    typewriter("- Deep sleep (physical recovery and body repair).", delay=0.02)
    typewriter("- REM sleep: dream phase and creativity boost.", delay=0.02)
    print()
    print()
    
    # === Understanding REM cycles and suggestion placement ===
    typewriter("REM phases, where most dreams occur, appear at:", delay=0.02)
    typewriter("- End of 1st cycle: around 75–90 minutes after falling asleep (~4500 seconds).", delay=0.02)
    typewriter("- End of 2nd cycle: around 165–180 minutes (~10800 seconds).", delay=0.02)
    typewriter("- End of 3rd cycle: around 255–270 minutes (~16200 seconds).", delay=0.02)
    typewriter("Audio suggestions should be placed just before or during these REM windows.", delay=0.02)
    print()
    print()

    # === Tips + Warnings combined ===
    typewriter("TIP & WARNING:", delay=0.005)
    typewriter("Using a progressive fade-out (~30 minutes) reduces the risk of waking abruptly at the end of a REM cycle.", delay=0.02)
    print()
    typewriter("Without fade-out: deep sleep is reduced, REM phase is stronger, which can increase creativity but also fatigue.", delay=0.02)
    print()
    typewriter("This technique was used by Salvador Dalí to boost creativity via interrupted micro-naps.", delay=0.02)
    typewriter("Source: Dalí, Salvador. *Les Rêveries d’un mangeur de pain* and studies on his “key technique.”", delay=0.005)
    print()
    typewriter("⚠️ Use occasionally to avoid chronic fatigue.", delay=0.02)
    print()
    print()

    # === Oniromancy ===
    typewriter("ONIROMANCY:", delay=0.005)
    typewriter("Oniromancy is the art of guiding dreams through targeted audio suggestions.", delay=0.02)
    typewriter("This process is based on psychology and REM cycles (not magic).", delay=0.02)
    typewriter("Audio suggestions should be played during identified REM windows.", delay=0.02)
    typewriter("Your own voice is more effective because the brain recognizes it as an internal thought, reducing resistance to suggestions.", delay=0.02)
    print()
    typewriter("Source: *Journal of Cognitive Neuroscience*, study on perception of internal voices, 2015.", delay=0.005)
    print()

    # === Choice to create audio suggestions ===
    typewriter("Do you want to create audio suggestions to guide your dreams? (y/n)\n", delay=0.02)
    choice = ""
    while choice not in ("y", "n"):
        choice = input("> ").strip().lower()

    if choice == "y":
        typewriter("\nVery well.", delay=0.02)
        typewriter("You can use free software like Audacity.", delay=0.02)
        typewriter("Record simple, affirmative, and positive sentences.", delay=0.02)
        typewriter("Some examples:", delay=0.02)
        print()
        typewriter('- "I am moving through a calm and bright place."', delay=0.02)
        typewriter('- "I am visiting a beautiful and peaceful place."', delay=0.02)
        typewriter('- "I remember my dreams upon waking."', delay=0.02)
        print()
        typewriter("\nSave your files in WAV format.", delay=0.02)
        typewriter("Place them in the folder: scripts/Assets/SFX/Suggests", delay=0.02)
        typewriter("They will be automatically integrated by the program.", delay=0.02)

        # Automatically open suggestions folder
        se_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Assets/SFX/Suggests"))
        os.startfile(se_path)

    # === Input for pink noise duration ===
    total_duration = typed_input("\nEnter total duration in seconds (e.g., 7200 for 2h): ")
    print()
    fade = typed_input("\nEnter fade-out duration in seconds (e.g., 1800 for 30 min): ")

    # === Launch pink_noise script ===
    print("\nLaunching pink noise script...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    pink_noise_path = os.path.join(script_dir, "bruit_rose.py")
    os.system(f'python "{pink_noise_path}" {total_duration} {fade}')
    
    # Stop sound once animation is finished
    winsound.PlaySound(None, winsound.SND_PURGE)

if __name__ == "__main__":
    main()

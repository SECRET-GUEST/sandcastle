[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Batch Script](https://img.shields.io/badge/script-batch-DDFF00)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
[![WinDdos](https://img.shields.io/badge/WinDdos-blue)](https://www.microsoft.com/en-us/windows)

```
███████╗ █████╗ ███╗   ██╗██████╗  ██████╗ █████╗ ███████╗████████╗██╗     ███████╗
██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║     ██╔════╝
███████╗███████║██╔██╗ ██║██║  ██║██║     ███████║███████╗   ██║   ██║     █████╗  
╚════██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══██║╚════██║   ██║   ██║     ██╔══╝  
███████║██║  ██║██║ ╚████║██████╔╝╚██████╗██║  ██║███████║   ██║   ███████╗███████╗
╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚══════╝
                                                                                   
```

![ALPHA](https://img.shields.io/badge/ALPHA-red)

# 🎧 **Pink Noise Generator**

## [Une version francaise est disponible dans la branche FR](https://github.com/SECRET-GUEST/sandcastle/tree/FR)
---
---

## 📌 **Overview**

This program generates **filtered pink noise**, scientifically recognized for improving the quality of deep sleep.
It can automatically integrate **personalized audio suggestions** at optimal times during REM sleep cycles to **influence and guide dreams**.

### Key Features

* 🎶 High-quality pink noise generation (44.1 kHz).
* 🌊 **Wave-like modulation** to sync with breathing (optional).
* 🥁 **Low-frequency kick** acting as a heart-rate metronome (optional).
* 🗣️ Automatic integration of **custom voice suggestions** (optional).
* ⏳ Smart placement of suggestions according to **REM cycles**.
* 🔄 **Controlled randomization** to avoid repetition and preserve pink noise.
* 🎚️ **Configurable fade-out** (recommended: 1800 s = 30 min).
* 📂 Output in `.wav` (final file + debug intermediates).
* ⚡ Automatic dependency installation (virtualenv or global).

---

## 🚀 **Usage**

1. **Run the program**
   Double-click:

```
START.bat
```

2. **If suggestions are enabled**

* Place your `.wav` files in:

```
scripts/Assets/SFX/Suggests/
```

* They will be automatically integrated and normalized into the final audio.

---

## 🖥 **Optional: Automatic PC Shutdown**

You can schedule your PC (Windows) to shut down automatically at the end of playback using:

```powershell
shutdown /s /t 8000
```

Where:

* `/s` = Full shutdown
* `/t` = Delay before shutdown (in seconds)

**Examples:**

* `shutdown /s /t 7200` → shutdown after **2 hours**
* `shutdown /s /t 14400` → shutdown after **4 hours**

**Cancel a scheduled shutdown:**

```powershell
shutdown /a
```

---

## 📂 **File Structure**

```
Project/
│   START.bat           → Launches the full program
│
└───scripts
   ├───Assets
   │   └───SFX
   │       ├───SE           → System sounds
   │       └───Suggests     → User voice suggestions (.wav)
   │
   └───src
       │   bruit_rose.py    → Pink noise generation + suggestion integration
       │   intro.py         → Intro explaining sleep cycles
       │   loadingSpinner.py→ Console loading animation
       │   requirements.txt → Auto-installed dependencies
```

---

## ⏳ **Cycles & Suggestion Placement**

Suggestions are automatically placed just before or during the REM phase of each \~90-minute sleep cycle:

| Cycle | REM start (approx.) | Suggestion placement | Time in seconds (min → max) |
| ----- | ------------------- | -------------------- | --------------------------- |
| 1     | 70–90 min           | \~1h15 – 1h30        | 4500 – 5400 s               |
| 2     | 160–180 min         | \~2h45 – 3h          | 9900 – 10800 s              |
| 3     | 250–270 min         | \~4h15 – 4h30        | 15300 – 16200 s             |

---

## ⚠️ **Disclaimer**

* Without fade-out, REM phases may be amplified → **more dreams, but less physical recovery**.
* Prolonged use may lead to **fatigue** or **sleep disturbances**.
* The impact of audio suggestions depends heavily on **individual sensitivity**.
* Guidance features (heart-rate or breathing synchronization) may feel disturbing for some sensitive users.
  👉 If you experience discomfort (palpitations, anxiety, unease), **disable these options**.

---

## 📜 **References**

* Ngo, Hong-Viet V., et al. [*Enhancing Slow Wave Sleep with Auditory Stimulation*](https://www.frontiersin.org/articles/10.3389/fnhum.2013.00871/full). *Frontiers in Human Neuroscience*, 2017.
* Dalí, Salvador. [*50 Secrets of Magic Craftsmanship (1948)*.](https://www.google.fr/books/edition/50_Secrets_of_Magic_Craftsmanship/0g6QlUiqwfcC?hl=fr&gbpv=0)
* [*Journal of Cognitive Neuroscience*, 2015 — Study on the perception of inner voices](https://direct.mit.edu/jocn/article/27/7/1308/28351/Perceiving-Inner-Speech-Voices-as-Internal-or).
* Walker, Matthew. [*Why We Sleep: Unlocking the Power of Sleep and Dreams*](https://en.wikipedia.org/wiki/Why_We_Sleep). Scribner, 2017.
* Carskadon, Mary A., & Dement, William C. [*Normal Human Sleep: An Overview*](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2656292/). *Principles and Practice of Sleep Medicine*, 2005.

---

💡 **Tip**: Use **your own voice** for suggestions. The brain recognizes it as an internal thought → stronger impact.

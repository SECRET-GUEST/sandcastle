[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Batch Script](https://img.shields.io/badge/script-batch-DDFF00)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
[![Windows](https://img.shields.io/badge/WINDOWS-blue)](https://www.microsoft.com/en-us/windows)

```
███████╗ █████╗ ███╗   ██╗██████╗  ██████╗ █████╗ ███████╗████████╗██╗     ███████╗
██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║     ██╔════╝
███████╗███████║██╔██╗ ██║██║  ██║██║     ███████║███████╗   ██║   ██║     █████╗  
╚════██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══██║╚════██║   ██║   ██║     ██╔══╝  
███████║██║  ██║██║ ╚████║██████╔╝╚██████╗██║  ██║███████║   ██║   ███████╗███████╗
╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚══════╝
                                                                                   
```

![ALPHA](https://img.shields.io/badge/ALPHA-red)

# 🎧 **Pink Noise Generator & Oniromancy**

## Une version francaise est disponible dans le dossier FR

---

## 📌 **Overview**

This program generates **filtered pink noise** to improve sleep quality, and can automatically integrate **audio suggestions** (voice, sounds) at the optimal times during REM sleep cycles to help **influence dreams (oniromancy)**.

The interface provides simple guidance on:

* **Sleep cycles** and their durations.
* The role of the **fade-out**.
* Automatic placement of audio suggestions.

---

## 🚀 **Usage**

1. **Run the program**

Double-click:

```
START.bat
```

*(No manual installation required — everything is handled automatically.)*

2. **Follow on-screen instructions**

* Enter the **total duration** of the pink noise (in seconds).
* Enter the **fade-out duration** (in seconds).
* Choose whether to **add voice suggestions**.

3. **If suggestions are enabled**

* Place your `.wav` files in:

```
scripts/Assets/SFX/Suggests/
```

* They will be automatically integrated and normalized in the final audio.

---

## 📂 **File Structure**

```
Project/
│   START.bat           → Launches the entire program
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

Suggestions are automatically placed just before or during the REM phase of each cycle (\~90 min):

| Cycle | REM Start (approx.) | Suggestion Placement |
| ----- | ------------------- | -------------------- |
| 1     | 70–90 min           | \~1h15 – 1h30        |
| 2     | 160–180 min         | \~2h45 – 3h          |
| 3     | 250–270 min         | \~4h15 – 4h30        |

---

## ⚠️ **Warning**

* Without fade-out, REM is amplified → more creativity but **less physical recovery**.
* Overusing this method can cause **fatigue and sleep disruption**.
* Inspired by Salvador Dalí’s micro-sleep technique (*Les Rêveries d’un mangeur de pain*).

---

## 📜 **References**

* Ngo, Hong-Viet V., et al. *Enhancing Slow Wave Sleep with Auditory Stimulation*. Frontiers in Human Neuroscience, 2017.
* Dalí, Salvador. *Les Rêveries d’un mangeur de pain*.
* *Journal of Cognitive Neuroscience*, 2015 — study on internal voice perception.

---

💡 **Tip**: Use your **own voice** for suggestions. The brain identifies it as an internal thought → stronger impact.


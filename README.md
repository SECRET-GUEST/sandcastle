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

# 🎧 **Pink Noise Generator & Oniromancy**

---

## 📌 **Aperçu**

Ce programme génère du **bruit rose filtré** afin d’améliorer la qualité du sommeil, et peut intégrer automatiquement des **suggestions audio** (voix, sons) aux moments optimaux des cycles de sommeil paradoxal (REM) afin d’**influencer les rêves (oniromancie)**.

L’interface fournit des explications simples sur :

* Les **cycles de sommeil** et leur durée.
* Le rôle du **fade-out**.
* Le placement automatique des suggestions audio.

---

## 🚀 **Utilisation**

1. **Lancer le programme**
   Double-cliquer sur :

```
START.bat
```

*(Aucune installation manuelle nécessaire — tout est géré automatiquement.)*

2. **Suivre les instructions affichées**

* Entrer la **durée totale** du bruit rose (en secondes).
* Entrer la **durée du fade-out** (en secondes).
* Choisir d’**ajouter ou non des suggestions vocales**.

3. **Si les suggestions sont activées**

* Placer vos fichiers `.wav` dans :

```
scripts/Assets/SFX/Suggests/
```

* Ils seront automatiquement intégrés et normalisés dans l’audio final.

---

## 🖥 **Optionnel : Arrêt automatique du PC**

Il est possible de programmer l’arrêt automatique du PC à la fin de la lecture du bruit rose :

```powershell
shutdown /s /t 8000
```

Où :

* `/s` = Arrêt complet du PC
* `/t` = Délai avant l’arrêt (en secondes)

**Exemples :**

* `shutdown /s /t 7200` → arrêt après **2 heures**
* `shutdown /s /t 14400` → arrêt après **4 heures**

**Annuler un arrêt programmé :**

```powershell
shutdown /a
```

---

## 📂 **Structure des fichiers**

```
Project/
│   START.bat           → Lance le programme complet
│
└───scripts
   ├───Assets
   │   └───SFX
   │       ├───SE           → Sons systèmes
   │       └───Suggests     → Suggestions vocales utilisateur (.wav)
   │
   └───src
       │   bruit_rose.py    → Génération du bruit rose + intégration suggestions
       │   intro.py         → Intro explicative cycles de sommeil
       │   loadingSpinner.py→ Animation de chargement console
       │   requirements.txt → Dépendances auto-installées
```

---

## ⏳ **Cycles & Placement des suggestions**

Les suggestions sont automatiquement placées juste avant ou pendant la phase REM de chaque cycle (\~90 min) :

| Cycle | Début REM (approx.) | Placement suggestion | Durée en secondes (min → max) |
| ----- | ------------------- | -------------------- | ----------------------------- |
| 1     | 70–90 min           | \~1h15 – 1h30        | 4500 – 5400 s                 |
| 2     | 160–180 min         | \~2h45 – 3h          | 9900 – 10800 s                |
| 3     | 250–270 min         | \~4h15 – 4h30        | 15300 – 16200 s               |

---

## ⚠️ **Avertissement**

* Sans fade-out, le REM est amplifié → plus de créativité mais **moins de récupération physique**.
* Une utilisation excessive peut provoquer **fatigue et perturbations du sommeil**.
* Inspiré de la technique des micro-siestes de Salvador Dalí (*Les Rêveries d’un mangeur de pain*).

---

## 📜 **Références**

* Ngo, Hong-Viet V., et al. *Enhancing Slow Wave Sleep with Auditory Stimulation*. Frontiers in Human Neuroscience, 2017.
* Dalí, Salvador. *Les Rêveries d’un mangeur de pain*.
* *Journal of Cognitive Neuroscience*, 2015 — étude sur la perception des voix internes.

---

💡 **Astuce** : Utilisez **votre propre voix** pour les suggestions. Le cerveau la perçoit comme une pensée interne → impact renforcé.

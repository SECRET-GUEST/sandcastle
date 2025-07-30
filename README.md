[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Batch Script](https://img.shields.io/badge/script-batch-DDFF00)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
[![Winddos](https://img.shields.io/badge/WINDOWS-blue)](https://www.microsoft.com/en-us/windows)


![ALPHA](https://img.shields.io/badge/ALPHA-red) 

# 🎧 **Générateur de Bruit Rose & Oniromancie**

## An English version of this README is available in the `ENG` folder.

## 📌 **Présentation**


Ce programme génère du **bruit rose filtré** pour améliorer la qualité du sommeil et peut intégrer automatiquement des **suggestions audio** (voix, sons) au moment optimal des cycles de sommeil REM, afin d’orienter vos rêves (oniromancie).

L’interface explique simplement :


* Les **cycles de sommeil** et leurs durées.
* Le rôle du **fade-out**.
* Le placement automatique des suggestions audio.


---



## 🚀 **Utilisation**


1. **Lancer le programme**

  Double-cliquez sur :



  ```

  START.bat

  ```



  *(Aucune installation manuelle nécessaire : tout est géré automatiquement.)*



2. **Suivre les instructions à l’écran**



  * Entrez la **durée totale** du bruit rose (en secondes).

  * Entrez la **durée du fade-out** (en secondes).

  * Choisissez si vous voulez **ajouter des suggestions vocales**.



3. **Si suggestions activées**



  * Placez vos fichiers `.wav` dans :



    ```

    scripts/Assets/SFX/Suggests/

    ```

  * Ils seront automatiquement intégrés et normalisés dans l’audio final.



---



## 📂 **Structure des fichiers**



```

Projet/
│   START.bat           → Lance tout le programme
│
└───scripts
   ├───Assets
   │   └───SFX
   │       ├───SE           → Sons système
   │       └───Suggests     → Suggestions audio utilisateur (.wav)
   │
   └───src
       │   bruit_rose.py    → Génération bruit rose + intégration suggestions
       │   intro.py         → Intro explicative cycles sommeil
       │   loadingSpinner.py→ Animation de chargement console
       │   requirements.txt → Dépendances auto-installées
```



---



## ⏳ **Cycles & Placement des suggestions**


Les suggestions sont automatiquement placées avant ou pendant la phase REM de chaque cycle (~90 min) :


| Cycle | Début REM (approx.) | Placement suggestions |
| ----- | ------------------- | --------------------- |
| 1     | 70–90 min           | ~1h15 – 1h30         |
| 2     | 160–180 min         | ~2h45 – 3h           |
| 3     | 250–270 min         | ~4h15 – 4h30         |


---

## ⚠️ **Avertissement**


* Sans fade-out, la phase REM est amplifiée → plus de créativité mais **moins de récupération physique**.

* Utiliser cette méthode trop souvent peut provoquer **fatigue et dérèglement du sommeil**.

* Inspiré des techniques de Salvador Dalí (*Les Rêveries d’un mangeur de pain*).



---


## 📜 **Références**



* Ngo, Hong-Viet V., et al. *Enhancing Slow Wave Sleep with Auditory Stimulation*. Frontiers in Human Neuroscience, 2017.

* Dalí, Salvador. *Les Rêveries d’un mangeur de pain*.

* *Journal of Cognitive Neuroscience*, 2015 — étude sur la perception des voix internes.


---



💡 **Astuce** : Utilisez votre **propre voix** pour les suggestions. Le cerveau l’identifie comme une pensée interne → impact renforcé.


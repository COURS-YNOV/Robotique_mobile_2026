#Robot Chat — ESP32-C6 / MicroPython

Système robotique mobile autonome télécommandé via WiFi.

---

## Table des matières

1. [Présentation](#présentation)
2. [Matériel requis](#matériel-requis)
3. [Architecture logicielle](#architecture-logicielle)
4. [Analyse fonctionnelle](#analyse-fonctionnelle)
5. [Brochage ESP32-C6](#brochage-esp32-c6)
6. [Bilan énergétique](#bilan-énergétique)
7. [Installation et déploiement](#installation-et-déploiement)
8. [Fonctionnalités à venir](#fonctionnalités-à-venir)

---

## Présentation

Le Robot Chat est un système robotique différentiel à deux roues motrices embarquant :

- un **radar ultrasonique oscillant** (HC-SR04 + servo SG90) pour la détection d'obstacles,
- un **serveur HTTP embarqué** pour la télécommande WiFi depuis n'importe quel navigateur,
- un **écran OLED** avec yeux de chat animés reflétant l'état du système,
- une logique de **sécurité timeout** : arrêt automatique si aucune commande reçue depuis 1 500 ms.

```
Télécommande WiFi ──► ESP32-C6 ──► L298N ──► 2 Moteurs DC
                          │
                    HC-SR04 + SG90 (radar 70°→110°)
                    OLED SSD1306 (yeux de chat)
```

---

## Matériel requis

| Composant | Rôle | Quantité |
|---|---|---|
| ESP32-C6 DevKit | Microcontrôleur principal (WiFi 6) | 1 |
| L298N H-Bridge | Driver moteurs DC | 1 |
| Moteur TT DC (boîte jaune 1:48) | Propulsion différentielle | 2 |
| HC-SR04 | Capteur ultrasonique | 1 |
| Servo SG90 | Rotation radar 70°→110° | 1 |
| OLED SSD1306 128×64 | Affichage (I²C) | 1 |
| PmodALS (ADC121S101) | Capteur luminosité (SPI) | 1 |
| LED + R 220 Ω | Indicateurs visuels | 2 |
| LiPo 2S 7,4 V 6 200 mAh | Alimentation principale | 1 |
| Résistances 1 kΩ / 2 kΩ | Pont diviseur ECHO HC-SR04 | 1 jeu |

> **Obligatoire** — Le signal ECHO du HC-SR04 est en 5 V.  
> Câblez un pont diviseur : `ECHO → R1(1kΩ) → GPIO20 → R2(2kΩ) → GND` (V_out = 3,33 V ✓)

---

## Architecture logicielle

```
📁 /
├── main.py           # Boucle principale (radar + WiFi + moteurs + OLED)
├── config.py         # Constantes GPIO, WiFi, paramètres radar
├── wifi_control.py   # connect_wifi() + WebController HTTP
├── radar.py          # Balayage servo non-bloquant (70°→110°, 3°/5ms)
├── motors.py         # MotorDriver différentiel (duty_u16)
├── servo.py          # Servo SG90 (duty_ns, 500–2500 µs)
├── ultrasonic.py     # UltrasonicSensor (time_pulse_us)
├── display.py        # Yeux de chat OLED (Normal / Alerte / Fermé)
├── ssd1306.py        # Driver OLED (framebuf)
├── als.py            # PmodALS SPI — intégration prévue
└── leds.py           # StatusLeds GPIO — intégration prévue
```

### Boucle principale (`main.py`)

```
Chaque 10 ms :
  ├── web.poll()          → serveur HTTP non-bloquant (timeout 0,02 s)
  ├── radar.update()      → avance servo d'un pas + lit distance HC-SR04
  ├── timeout check       → silence > 1 500 ms → command = "stop"
  ├── logique moteur      → applique cmd sauf si dist ≤ 20 cm en "forward"
  └── OLED (/ 120 ms)    → yeux + barre distance / vitesse / angle
```

### Interface WiFi

Le robot se connecte au réseau configuré dans `config.py` (mode **STA**).

| Route | Description |
|---|---|
| `GET /` | Interface mobile HTML (boutons + slider vitesse) |
| `GET /cmd?name=fwd&speed=55` | Commande moteur |
| `GET /status` | JSON `{distance, angle, command, speed}` |

---

## Analyse fonctionnelle

### Bête à cornes

```
   ┌─────────────┐               ┌──────────────────┐
   │ Utilisateur │               │  Environnement   │
   └──────┬──────┘               └────────┬─────────┘
          │                               │
          └───────────┬───────────────────┘
                      ▼
               ┌─────────────┐
               │  Chat Robot │
               └──────┬──────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │ Naviguer de manière autonome    │
        │ en évitant les obstacles        │
        └─────────────────────────────────┘
```

**Fonction globale** :  
> *Le Robot Chat doit permettre à l'utilisateur de disposer d'un agent mobile autonome capable d'explorer son environnement, d'éviter les obstacles par radar ultrasonique, d'afficher son état via des yeux de chat animés, et d'être télécommandé en temps réel via WiFi depuis un navigateur mobile.*

---

### Tableau des fonctions de service

| Réf. | Intitulé | Critère | Niveau | Flexibilité |
|---|---|---|---|---|
| **FP1** | Naviguer en évitant les obstacles | Arrêt si distance ≤ 20 cm | Obligatoire | F0 |
| **FP2** | Télécommande WiFi | Commandes fwd/bwd/left/right/stop | Obligatoire | F1 — latence < 500 ms |
| **FS1** | Balayage radar | Oscillation 70°→110°, 3°/5 ms, non-bloquant | Obligatoire | F0 |
| **FS2** | Mesure luminosité | PmodALS 8 bits (0–100 %) | Souhaité | F2 — ±5 % |
| **FS3** | Indicateurs visuels | OLED yeux animés + 2 LEDs, < 300 ms | Obligatoire | F1 |
| **FS4** | Signal sonore | Haut-parleur DAC/PWM, bip + miaulement | Souhaité | F3 |
| **FS5** | Déplacement différentiel | L298N, 0–100 % PWM par moteur | Obligatoire | F0 |
| **FC1** | Alimentation | Batterie 7,4 V → moteurs + régulateurs | Contrainte | F0 |
| **FC2** | Niveaux logiques 3,3 V | Pont diviseur ECHO HC-SR04 | Contrainte | F0 critique |
| **FC3** | Timeout sécurité | Stop automatique si silence > 1 500 ms | Obligatoire | F0 |

---

## Brochage ESP32-C6

| GPIO | Composant | Direction | Signal |
|---|---|---|---|
| 0 | LED 1 (R 220 Ω) | Sortie | Numérique |
| 1 | LED 2 (R 220 Ω) | Sortie | Numérique |
| 2 | PmodALS SCK | Sortie | SPI 1 MHz |
| 3 | PmodALS SDO (MISO) | Entrée | SPI 1 MHz |
| 4 | L298N IN1 | Sortie | Numérique |
| 5 | L298N IN2 | Sortie | Numérique |
| 7 | L298N IN3 | Sortie | Numérique |
| 10 | L298N IN4 | Sortie | Numérique |
| 11 | L298N ENB (moteur D) | Sortie | PWM 1 kHz |
| 15 | L298N ENA (moteur G) | Sortie | PWM 1 kHz |
| 18 | Servo SG90 | Sortie | PWM 50 Hz, duty_ns |
| 19 | HC-SR04 TRIG | Sortie | Impulsion 10 µs |
| 20 | HC-SR04 ECHO ⚠️ | Entrée | 3,3 V via pont div. |
| 21 | OLED SDA | Bidirectionnel | I²C 100 kHz |
| 22 | OLED SCL | Sortie | I²C 100 kHz |
| 23 | PmodALS CS | Sortie | SPI actif bas |

---

## Bilan énergétique

### Caractéristiques batterie et moteurs

| Paramètre | Valeur |
|---|---|
| Batterie | LiPo 2S — 7,4 V — 6 200 mAh — 50C |
| Capacité utile (décharge 80 %) | **4 960 mAh ≈ 5 000 mAh** |
| Énergie totale | 7,4 V × 6,2 Ah = **45,9 Wh** |
| Tension effective moteurs (55 % PWM) | (7,4 − 2,0) × 0,55 ≈ **3,0 V** |
| Courant moteur TT à vide (6 V) | 120 mA |
| Courant moteur TT nominal (6 V) | 300 mA |
| Courant moteur TT calage (6 V) | 800 mA |

### Consommation par composant

| Composant | Rail | I typique | I max |
|---|---|---|---|
| 2× Moteur TT (55 % PWM) | 7,4 V → L298N | 125 mA chacun | 720 mA (calage) |
| L298N logique | 5 V | 36 mA | 70 mA |
| Servo SG90 (radar) | 5 V | 60 mA | 500 mA |
| HC-SR04 | 5 V | 20 mA | 25 mA |
| ESP32-C6 (WiFi actif) | 3,3 V | 160 mA | 250 mA |
| OLED SSD1306 | 3,3 V | 25 mA | 30 mA |

> Rail 5 V total → **260 mA** → courant batterie : `260 × 5,0 / (7,4 × 0,80)` = **220 mA**

### Bilan par scénario

| Scénario | I moteurs | I électronique | **I TOTAL** | Puissance |
|---|---|---|---|---|
| Avance 55 % | 300 mA | 220 mA | **520 mA** | 3,8 W |
| Virage 55 % | 350 mA | 220 mA | **570 mA** | 4,2 W |
| Stop (moteurs à l'arrêt) | 0 mA | 220 mA | **220 mA** | 1,6 W |
| Calage (bref) | 1 440 mA | 220 mA | **1 660 mA** | 12,3 W |

**Mission typique** (60 % avance + 20 % virage + 20 % stop) :  
`I_moy = 0,60×520 + 0,20×570 + 0,20×220 ≈ **500 mA**`

### Autonomie calculée

| Scénario | Formule | Autonomie |
|---|---|---|
| Avance continue | 5 000 / 520 | **≈ 9 h 35 min** |
| Mission typique | 5 000 / 500 | **≈ 10 h 00 min** |
| Virage/évitement continu | 5 000 / 570 | **≈ 8 h 45 min** |
| Veille WiFi (stop) | 5 000 / 220 | **≈ 22 h 45 min** |

### Analyse du C-rate

| Paramètre | Valeur |
|---|---|
| C-rate batterie | 50C |
| Courant max théorique (50C) | 310 A |
| C-rate réel en pic (calage) | **0,27C** |
| C-rate réel en mission | **0,08C** |
| Marge | × 185 — très surdimensionné |

> La batterie 50C est conçue pour drones FPV / voitures RC (20–50C requis).  
> Pour ce robot, une **LiPo 2S 2 000 mAh 2C** suffirait (~3 h d'autonomie, ~10 €).  
> La 6 200 mAh apporte ~10 h d'autonomie, ce qui est pratique pour les séances de test.

---

## Installation et déploiement

### 1. Flasher MicroPython sur l'ESP32-C6

```bash
pip install esptool
esptool.py --chip esp32c6 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32c6 --port /dev/ttyUSB0 write_flash -z 0x0 micropython-esp32c6-xxx.bin
```

### 2. Configurer le WiFi

Éditer `config.py` avant l'upload :

```python
WIFI_SSID     = "NomDeVotreReseau"
WIFI_PASSWORD = "MotDePasseWiFi"
```

### 3. Uploader les fichiers (via Thonny ou mpremote)

```bash
# Ordre recommandé
mpremote cp ssd1306.py :ssd1306.py
mpremote cp config.py :config.py
mpremote cp ultrasonic.py servo.py radar.py motors.py als.py leds.py :/
mpremote cp display.py wifi_control.py :/
mpremote cp main.py :main.py   # en dernier — démarre au reboot
```

### 4. Vérification

Après reboot, la console affiche l'IP DHCP du robot.  
Ouvrir `http://<IP_ROBOT>` dans un navigateur sur le même réseau WiFi.

---

## Fonctionnalités à venir

| Fonctionnalité | Fichier | État |
|---|---|---|
| Mesure de luminosité + LEDs nuit | `als.py` + `leds.py` | Câblé — intégration `main.py` en cours |
| Signal sonore (bip / miaulement) | `speaker.py` à créer | Non implémenté |
| SSID/mdp hors versioning | `secrets.py` | À séparer de `config.py` |

---

## Licence

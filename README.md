# Robot Mobile Autonome

Robot mobile autonome à 4 roues basé sur ESP32, développé en C++ avec PlatformIO.

## Composants
- ESP32 MH-ET LIVE MiniKit
- 4× Moteurs DC + 2× Driver L298N
- HC-SR04 (ultrason) monté sur servo SG90
- HC-SR501 (PIR)
- Écran OLED 0.91" SSD1306

## Structure du repo
- code/        → Code source PlatformIO (C++)
- plans-3d/    → Fichiers CAO 
- docs/        → Document technique
- plans-elec   → Fichiers Fritzing

## Environnement de développement
- PlatformIO + Arduino framework
- Board : MH ET LIVE ESP32MiniKit
- Langage : C++

## Fonctionnement
Le robot utilise une machine à états finis (FSM) à 3 états :
- **MOVING** : déplacement libre, balayage ultrason via servo
- **TURNING** : virage à droite si obstacle < 15 cm
- **STOPPED** : arrêt d'urgence si mouvement détecté (PIR)
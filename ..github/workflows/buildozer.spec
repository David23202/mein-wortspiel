[app]
title = WortGuru
package.name = wortguru
package.domain = org.deinspiel

# Quelldateien einbinden
source.include_exts = py,png,jpg,kv,atlas
source.dir = .

# Version der App
version = 1.0

# Anforderungen für das Swipe-Wortspiel
requirements = python3,kivy==2.3.0,pillow

# Orientierung (nur Hochformat wie das echte Wort Guru)
orientation = portrait

# Android-spezifische Einstellungen
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

# Architektur (Nur arm64-v8a für stabilen, schnellen GitHub-Build)
android.archs = arm64-v8a

# Vollbildmodus aktivieren
android.fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 0

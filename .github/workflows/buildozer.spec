[app]
title = WortGuru
package.name = wortguru
package.domain = org.deinspiel

# Nur Python-Dateien einbinden, um Paketkonflikte zu vermeiden
source.include_exts = py
source.dir = .

version = 1.0

# Anforderungen: Nur das absolut Notwendige (ohne pillow)
requirements = python3,kivy==2.3.0

orientation = portrait

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 0

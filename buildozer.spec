# buildozer.spec — NeuroAgent APK
# Сборка на Linux-хосте (или через GitHub Actions): JDK 17, buildozer качает Android SDK/NDK сам.

[app]

title = NeuroAgent
package.name = neuroagent
package.domain = org.neuroagent
version = 1.0.0

source.dir = .
source.include_exts = py,json,png,jpg,atlas,ttf
source.exclude_dirs = bin,.buildozer,__pycache__,test
source.exclude_patterns = *.pyc,*.pyo

# requests нужен для llm.py; kivy — для UI
requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = False

[buildozer]

log_level = 2
warn_on_root = 1

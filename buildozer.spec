[app]

title = Analizador de Paleta
package.name = paletteanalyzer
package.domain = org.colorapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy,pillow,numpy,plyer,android

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.0
osx.is_catalyst = 0

# Android
android.api = 30
android.minapi = 24
android.ndk = 28c
android.sdk = 30
android.archs = arm64-v8a

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.enable_androidx = True

[app]

# (str) Title of your application
title = Kivy App

# (str) Package name
package.name = mykivyapp
# (int) Minimum API your APK / AAB will support.
android.minapi = 21
version = 0.1
android.numeric_version = 10213
# (str) Android NDK version to use. Recommended for modern builds.
android.ndk = 25b
# (str) Package domain (needed for android/ios packaging)
# IMPORTANT: You MUST change this from 'com.yourcompany' to a unique domain like 'com.example' or your own.
package.domain = com.company
android.permissions = INTERNET

# (str) Source code where the main.py lives
source.dir = kivyapp

presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png
# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav

# (str) Application versioning

# (list) Application requirements. Using a modern Kivy version.
requirements = python3,kivy

#
# OSX Specific (These settings are for macOS desktop builds, not Android)
#

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 2.3.0

#
# Android specific
#
# Removed hardcoded java_home - it will be auto-detected

# (str) Name of the main application file without the .py extension
# Assuming your main entry point file is 'main.py'
app.main = main

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Which artifact to build for a release build. 'aab' is required for the Play Store.
android.release_artifact = aab

#
# Keystore information for signing your release build.
# You must generate this keystore first using the keytool command.
#
android.release = True
# (str) The filename of your keystore file
# You must set the full path to your keystore file here.
android.release.keystore = kivyapp.keystore

android.release.keystore.alias = kivyapp-alias

# Removed passwords - they will be provided at build time or via config.json

# (int) Target Android API, should be as high as possible.
android.api = 34



# (int) Android NDK API to use. This is the minimum API your app will support.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use. 'master' is a stable branch.
p4a.branch = develop

# The following lines related to OpenSSL have been commented out as they are often
# not required and can cause build issues.
# p4a.local_recipes=openssl
# p4a.openssl_url=/opt/homebrew/opt/openssl@3

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy
# Uncomment to use a custom checkout
#ios.ios_deploy_dir = ../ios_deploy
# Or specify URL and branch
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# (bool) Whether or not to sign the code
ios.codesign.allowed = false

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
# Kivy Android App Builder - Generate Signed APK/AAB for Google Play Store

Build and sign Kivy Android apps for Google Play Store release with our automated APK/AAB builder. This template provides everything needed to create production-ready, signed Android apps from your Kivy Python code.

> This project is based on the [UV Project Template](https://github.com/Kiwisuki/UV-Project-Template)

## Why App Signing is Required for Google Play

Google requires all apps uploaded to the Play Store to be digitally signed with a certificate. This ensures:

- **App Authenticity**: Verifies the app publisher's identity
- **Integrity Protection**: Prevents unauthorized modifications
- **Update Security**: Ensures only you can update your app

Our template handles all signing requirements automatically, generating properly signed AAB files ready for Google Play Console upload.

## Features

- **Automated APK/AAB Building**: Create release-ready Android App Bundles
- **Keystore Management**: Automatic keystore creation and management
- **Google Play Store Ready**: Generate signed AAB files for Play Store
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Persistent Configuration**: Save settings to `config.json`

## Quick Start

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Configure Your App**:
   ```bash
   python wizard.py
   ```

3. **Build and Sign Your App**:
   ```bash
   python build_apk.py
   ```

4. **Upload to Google Play Console**:
   - Find your signed AAB in the `bin/` folder
   - Upload to Google Play Console

## Requirements

- Python
- Java JDK (for keytool and Android builds)
- Android SDK with build-tools
- Buildozer

## SEO Keywords

kivy android app, build kivy app, kivy apk, kivy aab, google play store, app signing, android app bundle, python android app, apk signer, aab generator, google play requirements, app certificate, keystore manager, automated apk build, python to android
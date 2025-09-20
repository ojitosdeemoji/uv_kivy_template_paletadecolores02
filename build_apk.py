#!/usr/bin/env python3
"""
Script to build and sign Kivy Android APKs for Google Play Store distribution.

This script automates the process of:
1. Cleaning previous builds
2. Creating a release APK using buildozer
3. Creating keystore files if needed
4. Signing the APK with provided keystore
5. Storing only the signed APK in the bin folder

The script will prompt for any required information and save it to config.json
for future use (config.json is in .gitignore to prevent accidental commits).
"""

import json
import os
import subprocess
import sys
from getpass import getpass
from shutil import which

CONFIG_FILE = "config.json"
BIN_FOLDER = "bin"


def load_config():
    """Load configuration from config.json if it exists."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    return {}


def save_config(config):
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error: Could not save config file: {e}")


def get_user_input(prompt, config_key, config, secret=False):
    """
    Get user input, using saved value from config if available.
    
    Args:
        prompt (str): Text to show the user
        config_key (str): Key to look for in config
        config (dict): Configuration dictionary
        secret (bool): Whether to hide input (for passwords)
    
    Returns:
        str: User input value
    """
    if config_key in config and config[config_key]:
        if secret:
            # For passwords, we still want to confirm or change them
            change = input(f"{prompt} [password saved] Change it? (y/N): ").strip().lower()
            if change in ['y', 'yes']:
                value = getpass(f"{prompt}: ")
                # Save to config for next time
                config[config_key] = value
                return value
            else:
                return config[config_key]
        else:
            use_saved = input(f"{prompt} [saved value: {config[config_key]}] Use saved value? (Y/n): ").strip().lower()
            if use_saved in ['', 'y', 'yes']:
                return config[config_key]
            else:
                value = input(f"{prompt}: ").strip()
                # Save to config for next time
                config[config_key] = value
                return value
    
    if secret:
        value = getpass(f"{prompt}: ")
    else:
        value = input(f"{prompt}: ").strip()
    
    # Save to config for next time
    config[config_key] = value
    return value


def find_apksigner(config):
    """
    Find apksigner in common locations, in PATH, or from config.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        str: Path to apksigner or None if not found
    """
    # First check if apksigner path is specified in config
    if "apksigner_path" in config and config["apksigner_path"]:
        apksigner_path = config["apksigner_path"]
        # Handle the @ prefix if present
        if apksigner_path.startswith('@'):
            apksigner_path = apksigner_path[1:]
        if os.path.exists(apksigner_path):
            return apksigner_path
        else:
            print(f"Warning: Configured apksigner path not found: {apksigner_path}")
    
    # Common locations for apksigner
    common_paths = [
        # Android SDK locations
        "~/Android/Sdk/build-tools/*/apksigner",
        "~/AppData/Local/Android/Sdk/build-tools/*/apksigner.bat",
        "~/Library/Android/sdk/build-tools/*/apksigner",
        "/usr/local/android-sdk/build-tools/*/apksigner",
        "/opt/android-sdk/build-tools/*/apksigner",
        # Direct PATH search
        "apksigner",
        "apksigner.bat"
    ]
    
    # Check if apksigner is in PATH
    apksigner_path = which("apksigner")
    if apksigner_path:
        return apksigner_path
    
    # Check common paths
    import glob
    for pattern in common_paths:
        # Expand user home directory
        expanded_pattern = os.path.expanduser(pattern)
        matches = glob.glob(expanded_pattern)
        if matches:
            # Return the latest version (assuming higher version numbers are better)
            matches.sort(reverse=True)
            return matches[0]
    
    return None


def run_command(command, description, show_outputs=True):
    """
    Run a shell command and handle errors.
    
    Args:
        command (str): Command to run
        description (str): Description of what the command does
        show_outputs (bool): Whether to show command output in real-time
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{description}")
    print(f"Running: {command}")
    
    try:
        if show_outputs:
            # Show outputs in real-time
            result = subprocess.run(command, shell=True, check=True)
        else:
            # Capture outputs
            result = subprocess.run(command, shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  text=True)
            if result.stdout:
                print(result.stdout)
        
        print("Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if not show_outputs and e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def get_apk_info():
    """
    Get APK information from buildozer.spec file.
    
    Returns:
        dict: Dictionary with package_name, version, and other info
    """
    info = {
        'package_name': 'mykivyapp',
        'version': '0.1',
        'package_domain': 'com.company',
        'keystore': 'kivyapp.keystore',
        'keystore_alias': 'kivyapp-alias'
    }
    
    try:
        with open('buildozer.spec', 'r') as f:
            content = f.read()
            
        # Extract information using simple string matching
        for line in content.split('\n'):
            if line.startswith('package.name') and not line.startswith('#'):
                info['package_name'] = line.split('=')[1].strip()
            elif line.startswith('version') and not line.startswith('#'):
                info['version'] = line.split('=')[1].strip()
            elif line.startswith('package.domain') and not line.startswith('#'):
                info['package_domain'] = line.split('=')[1].strip()
            elif line.startswith('android.release.keystore') and not line.startswith('#'):
                info['keystore'] = line.split('=')[1].strip()
            elif line.startswith('android.release.keystore.alias') and not line.startswith('#'):
                info['keystore_alias'] = line.split('=')[1].strip()
                
    except Exception as e:
        print(f"Warning: Could not read buildozer.spec: {e}")
        print("Using default values.")
    
    return info


def create_keystore(config):
    """
    Create a new keystore file using keytool.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        tuple: (keystore_path, keystore_alias, keystore_password, key_password) or (None, None, None, None) if failed
    """
    print("\n--- CREATING NEW KEYSTORE ---")
    
    # Check if keytool is available
    if not which("keytool"):
        print("Error: keytool not found. Please ensure Java JDK is installed and in your PATH.")
        return None, None, None, None
    
    # Get keystore information from user or config
    keystore_path = get_user_input(
        "Keystore file path (e.g., myapp.keystore)", 
        "keystore_path", 
        config
    )
    
    if not keystore_path:
        print("Keystore path is required.")
        return None, None, None, None
    
    # If file already exists, ask if user wants to use it
    if os.path.exists(keystore_path):
        use_existing = input(f"Keystore file already exists at {keystore_path}. Use existing? (Y/n): ").strip().lower()
        if use_existing not in ['', 'y', 'yes']:
            print("Please provide a different keystore path.")
            return None, None, None, None
        else:
            # Get existing keystore info
            keystore_alias = get_user_input(
                "Keystore alias",
                "keystore_alias",
                config
            )
            
            keystore_password = get_user_input(
                "Keystore password",
                "keystore_password",
                config,
                secret=True
            )
            
            key_password = get_user_input(
                "Key password (if different from keystore password)",
                "key_password",
                config,
                secret=True
            )
            
            if not key_password:
                key_password = keystore_password
                
            return keystore_path, keystore_alias, keystore_password, key_password
    
    # Create new keystore
    print("Creating new keystore...")
    
    keystore_alias = get_user_input(
        "Keystore alias (e.g., myapp-alias)",
        "keystore_alias",
        config
    )
    
    if not keystore_alias:
        keystore_alias = "android-release"
    
    keystore_password = get_user_input(
        "Keystore password (minimum 6 characters)",
        "keystore_password",
        config,
        secret=True
    )
    
    if len(keystore_password) < 6:
        print("Error: Keystore password must be at least 6 characters.")
        return None, None, None, None
    
    key_password = get_user_input(
        "Key password (minimum 6 characters, if different from keystore password)",
        "key_password",
        config,
        secret=True
    )
    
    if not key_password:
        key_password = keystore_password
    elif len(key_password) < 6:
        print("Error: Key password must be at least 6 characters.")
        return None, None, None, None
    
    # Get additional information for the certificate from config or user
    print("\nCertificate information (used for app signing):")
    
    first_name = config.get("cert_first_name", "")
    if first_name:
        use_saved = input(f"First and Last Name [saved value: {first_name}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            first_name = input("First and Last Name (e.g., John Doe): ").strip()
    else:
        first_name = input("First and Last Name (e.g., John Doe): ").strip()
    
    if not first_name:
        first_name = "Unknown"
    config["cert_first_name"] = first_name
    
    org_unit = config.get("cert_org_unit", "")
    if org_unit:
        use_saved = input(f"Organizational Unit [saved value: {org_unit}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            org_unit = input("Organizational Unit (e.g., Development Team): ").strip()
    else:
        org_unit = input("Organizational Unit (e.g., Development Team): ").strip()
    
    if not org_unit:
        org_unit = "Unknown"
    config["cert_org_unit"] = org_unit
    
    org = config.get("cert_org", "")
    if org:
        use_saved = input(f"Organization [saved value: {org}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            org = input("Organization (e.g., My Company): ").strip()
    else:
        org = input("Organization (e.g., My Company): ").strip()
    
    if not org:
        org = "Unknown"
    config["cert_org"] = org
    
    city = config.get("cert_city", "")
    if city:
        use_saved = input(f"City or Locality [saved value: {city}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            city = input("City or Locality (e.g., San Francisco): ").strip()
    else:
        city = input("City or Locality (e.g., San Francisco): ").strip()
    
    if not city:
        city = "Unknown"
    config["cert_city"] = city
    
    state = config.get("cert_state", "")
    if state:
        use_saved = input(f"State or Province [saved value: {state}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            state = input("State or Province (e.g., CA): ").strip()
    else:
        state = input("State or Province (e.g., CA): ").strip()
    
    if not state:
        state = "Unknown"
    config["cert_state"] = state
    
    country = config.get("cert_country", "")
    if country:
        use_saved = input(f"Country code [saved value: {country}] Use saved value? (Y/n): ").strip().lower()
        if use_saved in ['', 'y', 'yes']:
            pass
        else:
            country = input("Two-letter country code (e.g., US): ").strip()
    else:
        country = input("Two-letter country code (e.g., US): ").strip()
    
    if not country or len(country) != 2:
        print("Warning: Country code should be two letters. Using XX as default.")
        country = "XX"
    config["cert_country"] = country
    
    # Create the keystore using keytool
    keytool_command = (
        f'keytool -genkey -v -keystore "{keystore_path}" '
        f'-alias "{keystore_alias}" '
        f'-keyalg RSA -keysize 2048 -validity 10000 '
        f'-storepass "{keystore_password}" '
        f'-keypass "{key_password}" '
        f'-dname "CN={first_name}, OU={org_unit}, O={org}, L={city}, ST={state}, C={country}"'
    )
    
    print("\nGenerating keystore with keytool...")
    if not run_command(keytool_command, "Creating keystore", show_outputs=False):
        print("Failed to create keystore.")
        return None, None, None, None
    
    print(f"Keystore created successfully at: {keystore_path}")
    return keystore_path, keystore_alias, keystore_password, key_password


def build_apk(show_outputs=True):
    """Build the release APK using buildozer."""
    print("\n--- CLEANING PREVIOUS BUILDS ---")
    if not run_command("buildozer android clean", "Cleaning previous builds", show_outputs):
        return False
    
    print("\n--- BUILDING RELEASE APK ---")
    if not run_command("buildozer android release", "Building release APK", show_outputs):
        return False
    
    return True


def find_unsigned_apk():
    """
    Find the unsigned APK/AAB file in the bin folder.
    
    Returns:
        str: Path to the unsigned APK/AAB file or None if not found
    """
    # Try to find any release file in bin folder
    import glob
    release_files = glob.glob(os.path.join(BIN_FOLDER, "*-release.*"))
    if release_files:
        # Prefer AAB files over APK files
        aab_files = [f for f in release_files if f.endswith('.aab')]
        if aab_files:
            return aab_files[0]
        else:
            return release_files[0]
    
    print(f"Error: No release APK/AAB found in {BIN_FOLDER} directory.")
    return None


def sign_apk(config, show_outputs=True):
    """
    Sign the APK with the provided keystore.
    
    Args:
        config (dict): Configuration dictionary
        show_outputs (bool): Whether to show command output in real-time
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get APK information
    apk_info = get_apk_info()
    
    # Find unsigned APK
    unsigned_path = find_unsigned_apk()
    if not unsigned_path:
        return False
    
    print(f"Found unsigned APK: {unsigned_path}")
    
    # Find apksigner
    apksigner_path = find_apksigner(config)
    if not apksigner_path:
        print("Error: Could not find apksigner. Please ensure Android SDK is installed and build-tools are available.")
        print("You can also:")
        print("1. Set the ANDROID_HOME environment variable to help locate it")
        print("2. Set apksigner_path in config.json (can start with @ for direct path)")
        return False
    
    print(f"Found apksigner at: {apksigner_path}")
    
    # Save apksigner path to config for future use
    config["apksigner_path"] = apksigner_path
    
    # Get keystore information from config or user
    keystore_path = config.get("keystore_path", "")
    if not keystore_path or not os.path.exists(keystore_path):
        keystore_path = get_user_input(
            "Keystore file path", 
            "keystore_path", 
            config
        )
    
    if not os.path.exists(keystore_path):
        # Offer to create a new keystore
        create_new = input(f"Keystore file not found at {keystore_path}. Create a new one? (Y/n): ").strip().lower()
        if create_new in ['', 'y', 'yes']:
            keystore_result = create_keystore(config)
            if keystore_result[0] is None:
                return False
            keystore_path, keystore_alias, keystore_password, key_password = keystore_result
        else:
            print("Cannot sign APK without a valid keystore.")
            return False
    else:
        # Use existing keystore from config
        keystore_alias = get_user_input(
            f"Keystore alias",
            "keystore_alias",
            config
        )
        if not keystore_alias:
            keystore_alias = apk_info['keystore_alias']
        
        keystore_password = get_user_input(
            "Keystore password",
            "keystore_password",
            config,
            secret=True
        )
        
        key_password = get_user_input(
            "Key password (if different from keystore password)",
            "key_password",
            config,
            secret=True
        )
        
        if not key_password:
            key_password = keystore_password
    
    # Construct signed APK filename
    # Extract the base name without the -release part
    base_name = os.path.basename(unsigned_path)
    if base_name.endswith('-release.aab'):
        signed_apk_name = base_name.replace('-release.aab', '-signed.aab')
    elif base_name.endswith('-release.apk'):
        signed_apk_name = base_name.replace('-release.apk', '-signed.apk')
    else:
        # Fallback
        signed_apk_name = base_name.replace('-release', '-signed')
    
    signed_path = os.path.join(BIN_FOLDER, signed_apk_name)
    
    # Sign the APK
    sign_command = (
        f'"{apksigner_path}" sign '
        f'--ks "{keystore_path}" '
        f'--ks-key-alias "{keystore_alias}" '
        f'--ks-pass pass:"{keystore_password}" '
        f'--key-pass pass:"{key_password}" '
        f'--min-sdk-version 21 '
        f'--out "{signed_path}" '
        f'"{unsigned_path}"'
    )
    
    print("\n--- SIGNING APK ---")
    if not run_command(sign_command, "Signing APK", show_outputs):
        return False
    
    # Remove unsigned APK to save space and avoid confusion
    try:
        os.remove(unsigned_path)
        print(f"Removed unsigned APK: {unsigned_path}")
    except Exception as e:
        print(f"Warning: Could not remove unsigned APK: {e}")
    
    print(f"\nSUCCESS! Signed APK is available at: {signed_path}")
    return True


def main():
    """Main function to build and sign the APK."""
    print("=== Kivy APK Builder and Signer ===")
    print("This script will build and sign your Kivy app for Google Play Store.")
    
    # Check if we're in the right directory
    if not os.path.exists('buildozer.spec'):
        print("Error: buildozer.spec not found in current directory.")
        print("Please run this script from your Kivy project root directory.")
        return 1
    
    # Load existing configuration
    config = load_config()
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Build and sign APK (full process)")
    print("2. Sign existing APK only")
    choice = input("Enter your choice (1/2): ").strip()
    
    if choice == "2":
        # Sign only
        show_outputs_input = input("Show detailed command outputs? (Y/n): ").strip().lower()
        show_outputs = show_outputs_input not in ['n', 'no']
        
        # Sign the APK
        if not sign_apk(config, show_outputs):
            print("Failed to sign APK. Exiting.")
            return 1
    else:
        # Full build and sign process
        # Ask if user wants to see command outputs
        show_outputs_input = input("Show detailed command outputs? (Y/n): ").strip().lower()
        show_outputs = show_outputs_input not in ['n', 'no']
        
        # Build the APK
        if not build_apk(show_outputs):
            print("Failed to build APK. Exiting.")
            return 1
        
        # Sign the APK
        if not sign_apk(config, show_outputs):
            print("Failed to sign APK. Exiting.")
            return 1
    
    # Save configuration
    save_config(config)
    
    print("\n=== PROCESS COMPLETED SUCCESSFULLY ===")
    print("Your signed APK is ready for Google Play Store upload!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
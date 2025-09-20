#!/usr/bin/env python3
"""
Wizard script to help configure buildozer.spec for Kivy Android apps.

This script provides an interactive way to update important buildozer settings
like app name, package name, version, permissions, etc.
"""

import os
import re


def load_buildozer_config():
    """Load the buildozer.spec file content."""
    if not os.path.exists('buildozer.spec'):
        print("Error: buildozer.spec not found in current directory.")
        return None
    
    try:
        with open('buildozer.spec', 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading buildozer.spec: {e}")
        return None


def save_buildozer_config(content):
    """Save the updated buildozer.spec file content."""
    try:
        with open('buildozer.spec', 'w') as f:
            f.write(content)
        print("buildozer.spec updated successfully!")
        return True
    except Exception as e:
        print(f"Error saving buildozer.spec: {e}")
        return False


def update_config_value(content, key, new_value):
    """
    Update a configuration value in the buildozer.spec content.
    
    Args:
        content (str): The content of buildozer.spec
        key (str): The configuration key to update
        new_value (str): The new value to set
        
    Returns:
        str: Updated content
    """
    # Create pattern to match the key and its value
    pattern = rf'({key}\s*=\s*)(.*)'
    
    # Check if the key already exists and is not commented out
    match = re.search(rf'^{key}\s*=', content, re.MULTILINE)
    if match:
        # Update existing uncommented value
        content = re.sub(pattern, rf'\1{new_value}', content, count=1, flags=re.MULTILINE)
    else:
        # Check if the key exists but is commented out
        commented_match = re.search(rf'^#\s*{key}\s*=', content, re.MULTILINE)
        if commented_match:
            # Uncomment and update
            content = re.sub(rf'^#\\s*{key}\\s*=.*', f'{key} = {new_value}', content, count=1, flags=re.MULTILINE)
        else:
            # Add new entry in the [app] section
            content = re.sub(r'($app$)', '\\1\\n' + key + ' = ' + new_value + '\\n', content, count=1)
    
    return content


def get_current_value(content, key):
    """
    Get the current value of a configuration key.
    
    Args:
        content (str): The content of buildozer.spec
        key (str): The configuration key to find
        
    Returns:
        str: Current value or None if not found
    """
    match = re.search(rf'^{key}\s*=\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def wizard_menu():
    """Display the main wizard menu."""
    print("\n=== Buildozer Configuration Wizard ===")
    print("1. App Title")
    print("2. Package Name")
    print("3. Package Domain")
    print("4. Version")
    print("5. Android API Level")
    print("6. Permissions")
    print("7. App Orientation")
    print("8. View Current Configuration")
    print("0. Exit")
    print("=" * 40)


def update_app_title(content):
    """Update the app title."""
    current = get_current_value(content, 'title')
    print(f"\nCurrent App Title: {current or 'Not set'}")
    new_title = input("Enter new app title (or press Enter to keep current): ").strip()
    
    if new_title:
        return update_config_value(content, 'title', new_title)
    return content


def update_package_name(content):
    """Update the package name."""
    current = get_current_value(content, 'package.name')
    print(f"\nCurrent Package Name: {current or 'Not set'}")
    new_name = input("Enter new package name (or press Enter to keep current): ").strip()
    
    if new_name:
        return update_config_value(content, 'package.name', new_name)
    return content


def update_package_domain(content):
    """Update the package domain."""
    current = get_current_value(content, 'package.domain')
    print(f"\nCurrent Package Domain: {current or 'Not set'}")
    print("Note: This should be a unique domain like 'com.yourcompany' or 'org.yourname'")
    new_domain = input("Enter new package domain (or press Enter to keep current): ").strip()
    
    if new_domain:
        return update_config_value(content, 'package.domain', new_domain)
    return content


def update_version(content):
    """Update the app version."""
    current_version = get_current_value(content, 'version')
    current_numeric = get_current_value(content, 'android.numeric_version')
    print(f"\nCurrent Version: {current_version or 'Not set'}")
    print(f"Current Numeric Version: {current_numeric or 'Not set'}")
    
    new_version = input("Enter new version (e.g., 1.0.0) (or press Enter to keep current): ").strip()
    if new_version:
        content = update_config_value(content, 'version', new_version)
        
        # Generate a simple numeric version (format: major*10000 + minor*100 + patch)
        numeric_version = "1"  # Default
        try:
            parts = new_version.split('.')
            if len(parts) >= 1:
                major = int(parts[0]) if parts[0].isdigit() else 0
                minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                numeric_version = str(major * 10000 + minor * 100 + patch)
                if numeric_version == "0":
                    numeric_version = "1"
        except:
            pass
            
        content = update_config_value(content, 'android.numeric_version', numeric_version)
    
    return content


def update_api_level(content):
    """Update Android API level."""
    current_api = get_current_value(content, 'android.api')
    current_min_api = get_current_value(content, 'android.minapi')
    current_ndk_api = get_current_value(content, 'android.ndk_api')
    
    print(f"\nCurrent API Level: {current_api or 'Not set'}")
    print(f"Current Minimum API: {current_min_api or 'Not set'}")
    print(f"Current NDK API: {current_ndk_api or 'Not set'}")
    
    print("\nRecommended values:")
    print("API Level: 34 (Android 14)")
    print("Minimum API: 21 (Android 5.0)")
    print("NDK API: 21")
    
    new_api = input("Enter new API level (or press Enter to keep current): ").strip()
    if new_api:
        content = update_config_value(content, 'android.api', new_api)
    
    new_min_api = input("Enter new minimum API level (or press Enter to keep current): ").strip()
    if new_min_api:
        content = update_config_value(content, 'android.minapi', new_min_api)
        content = update_config_value(content, 'android.ndk_api', new_min_api)  # Usually same as minapi
    
    return content


def update_permissions(content):
    """Update Android permissions."""
    current = get_current_value(content, 'android.permissions')
    print(f"\nCurrent Permissions: {current or 'Not set'}")
    print("\nCommon permissions:")
    print("INTERNET - Required for network access")
    print("WRITE_EXTERNAL_STORAGE - For file access")
    print("CAMERA - For camera access")
    print("ACCESS_FINE_LOCATION - For precise location")
    print("ACCESS_COARSE_LOCATION - For approximate location")
    
    print("\nEnter permissions separated by commas (e.g., INTERNET,CAMERA,LOCATION)")
    print("Leave empty to keep current permissions")
    new_perms = input("Enter new permissions: ").strip()
    
    if new_perms:
        return update_config_value(content, 'android.permissions', new_perms)
    return content


def update_orientation(content):
    """Update app orientation."""
    current = get_current_value(content, 'orientation')
    print(f"\nCurrent Orientation: {current or 'Not set'}")
    print("\nOptions:")
    print("portrait - Portrait mode only")
    print("landscape - Landscape mode only")
    print("all - All orientations")
    
    new_orientation = input("Enter new orientation (portrait/landscape/all) (or press Enter to keep current): ").strip()
    
    if new_orientation in ['portrait', 'landscape', 'all']:
        return update_config_value(content, 'orientation', new_orientation)
    elif new_orientation:
        print("Invalid orientation. Keeping current value.")
    
    return content


def view_configuration(content):
    """Display current configuration."""
    print("\n=== Current Buildozer Configuration ===")
    
    keys_to_show = [
        'title',
        'package.name',
        'package.domain',
        'version',
        'android.numeric_version',
        'android.api',
        'android.minapi',
        'android.ndk_api',
        'android.permissions',
        'orientation'
    ]
    
    for key in keys_to_show:
        value = get_current_value(content, key)
        display_key = key.replace('android.', '').replace('.', ' ').title()
        print(f"{display_key:20}: {value or 'Not set'}")


def main():
    """Main wizard function."""
    print("Welcome to the Buildozer Configuration Wizard!")
    print("This tool will help you configure your buildozer.spec file.")
    
    content = load_buildozer_config()
    if content is None:
        return 1
    
    while True:
        wizard_menu()
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == '0':
            print("Exiting wizard...")
            break
        elif choice == '1':
            content = update_app_title(content)
        elif choice == '2':
            content = update_package_name(content)
        elif choice == '3':
            content = update_package_domain(content)
        elif choice == '4':
            content = update_version(content)
        elif choice == '5':
            content = update_api_level(content)
        elif choice == '6':
            content = update_permissions(content)
        elif choice == '7':
            content = update_orientation(content)
        elif choice == '8':
            view_configuration(content)
        else:
            print("Invalid choice. Please try again.")
            continue
        
        # Save after each change
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            if save_buildozer_config(content):
                print("Changes saved!")
            else:
                print("Failed to save changes.")
    
    return 0


if __name__ == "__main__":
    exit(main())

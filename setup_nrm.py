import os
import sys
import platform
import subprocess


def install_requirements():
    """Install the required packages from requirements.txt."""
    try:
        # Install the required packages from requirements.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--user'])
        print("Successfully installed required packages.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        sys.exit(1)


def create_batch_file(nrm_path):
    """Create a batch file for Windows."""
    batch_file_content = f'@echo off\npython "{nrm_path}" %*\n'
    batch_file_path = os.path.join(os.environ['USERPROFILE'], 'nrm.bat')

    with open(batch_file_path, 'w') as f:
        f.write(batch_file_content)

    print(f'Batch file created at: {batch_file_path}')
    print('You may need to add the directory to your PATH if it is not already included.')
    import data
    data.main()


def create_shell_script(nrm_path):
    """Create a shell script for Linux or macOS."""
    shell_script_content = f'#!/bin/bash\npython "{nrm_path}" "$@"\n'
    shell_script_path = '/usr/local/bin/nrm'

    with open(shell_script_path, 'w') as f:
        f.write(shell_script_content)

    os.chmod(shell_script_path, 0o755)  # Make it executable
    import data
    data.main()
    print('[SUCCESS] You can run it by typing `nrm` in your terminal.')


def main():
    """Main function to orchestrate the setup process."""
    # Path to the nrm.py file
    nrm_path = os.path.abspath("nrm.py")

    if not os.path.isfile(nrm_path):
        print("[ERROR] The nrm.py file does not exist in the current directory.")
        sys.exit(1)

    # Install requirements
    install_requirements()

    # Detect the operating system
    os_type = platform.system()

    if os_type == 'Windows':
        create_batch_file(nrm_path)
    elif os_type in ['Linux', 'Darwin']:  # Darwin is for macOS
        create_shell_script(nrm_path)
    else:
        print("Unsupported operating system. This script only supports Windows, macOS, and Linux.")


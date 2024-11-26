
import os # operating sys stuff
import random # random verify codes
import zipfile # zip manager
import urllib3 # download package
from nrmengine import upload # upload package
from nrmengine.packages import search_package, insert_data, search_owner, delete_package, search_link, edit_package # get package
from nrmengine.sendmail import send_email # send package
import readline  # up and down keys shortcuts
import sys # system stuff
import shutil # delete stuff
import re # email thing
from colorama import Fore, Style, init # colored text baby
import subprocess
import time
# Initialize Colorama
init(autoreset=True)

# Help text for commands
help_text = """--------------------------------------------------------------
List of commands for NRM v0.0.1:
- version: version of NRM.
- credits: people who made NRM.
- help <commands>: show related help in specific <commands>.
- installed: shows installed packages.
- <file.nrm> <arg1(if needed)> <arg2(if needed)> ...: run a nrm file.
- update <optional: specific version>: update NRM; for specific version (Example v0.0.1 write: "update 0.0.1")
- upload <dir> <mail>: upload a package into the NRM library. More info at nrm.us.to
- upload-template: creates a template for uploading package.
- manage-packages <mail> (or manage-package <mail>): edit your uploaded package via mail.
- install <package1> <package2> ...: installs (a) package(s) from NRM library.
- uninstall <package1> <package2> ...: uninstalls (a) package(s) on the computer.
- reinstall <package1> <package2> ...: reinstalls (a) package(s).
- alias <1:mode> <2:command> <2:shortcut>: Creates a shortcut for a frequently used (or long) command.
-> *Alias modes*
 + -show: show all shortcuts you've made.
 + -manage: manage your shortcuts.
- exit: exits NRM (runtime).
- clean: clears terminal/cmd.

Need help? Check out our faqs at http://use-nrm.us.to/faq
--------------------------------------------------------------"""

# Unpack shortcuts._nrm_
try:
    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'r') as f:
        shortcuts = f.read().split('\n')
except FileNotFoundError:
    pass

commands = ["help", "credits", "upload", "version", "installed", "update", "install", "uninstall", "reinstall", "manage-packages", "manage-package","clean", "alias", "upload-template"]
subcommands = ["-runtime"]

def clean_console():
    """Clears the console output."""
    if os.name == 'nt':  # For Windows
        subprocess.run('cls')
    else:  # For Unix/Linux/Mac
        subprocess.run('clear')

def reinstall(package):
    """Reinstalls package."""
    uninstall_package(package)
    install_package(package)

    return "s"

def print_progress_bar(iteration, total, length=50):
    """Print a progress bar to the console."""
    percent = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '*' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r[PROGRESS] |{bar}| {percent:.2f}%')
    sys.stdout.flush()

def zip_folder(folder_path, zip_file_path):
    """Zip a directory for upload."""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        total_files = sum(len(files) for _, _, files in os.walk(folder_path))
        current_file = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
                current_file += 1
                print_progress_bar(current_file, total_files)  # Update progress bar
    
    print()  # New line after progress bar completion
    return f"[INFO] Folder '{folder_path}' has been zipped into '{zip_file_path}'."

def is_valid_email(email):
    """Validate the email address using a regex pattern."""
    # Ensure the input is a string
    if not isinstance(email, str):
        return False
    
    # Define the regex pattern for a valid email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Use re.match to check if the email matches the pattern
    return re.match(pattern, email) is not None

def unzip_file(zip_file_path, destination):
    """Unzips the downloaded zip file into the destination directory."""
    try:
        os.makedirs(destination, exist_ok=True)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(destination)
        return f"[INFO] Unzipped package to {destination}"
    except Exception as e:
        return Fore.RED + f"[ERROR] An error occurred while unzipping: {e}\nThe module might have some problem with it's zip, please contact the dev at " + Fore.YELLOW + search_package(os.path.splitext(os.path.basename(zip_file_path))[0])
    
def download_file(name, url, zip_path="packages/my_package.zip"):
    """Downloads a file from a URL and unzips it."""
    # Ensure name is used correctly
    package_name = name  # Assuming name is the package name directly
    zip_dir = os.path.dirname(zip_path)
    os.makedirs(zip_dir, exist_ok=True)
    temp_file_path = f'{package_name}.zip'  # Use package_name directly

    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url)
        if response.status == 200:
            with open(temp_file_path, 'wb') as f:
                f.write(response.data)
            sys.stdout.write(f"[INFO] Downloaded data from {url} to {temp_file_path}\n")
            sys.stdout.write(unzip_file(temp_file_path, package_name) + "\n")  # Unzip with the correct name
            shutil.move(package_name, 'packages')
            return Fore.GREEN + f"[SUCCESS] Downloading proccess completed."
        else:
            sys.stdout.write(Fore.YELLOW + f"[WARNING] Failed to download file. HTTP Status: {response.status}\n")

    except Exception as e:
        sys.stdout.write(Fore.RED + f"[ERROR] An error occurred: {e}\n")

def verify_email(email):
    """Handle email verification process."""
    if email is None:
        email = input("Enter your email: ")
        if email.lower() == 'x':
            return "Canceled Operation."
    
    clean_console()
    sys.stdout.write("******************************************************\n")
    sys.stdout.write("**VERIFY YOUR EMAIL TO CONTINUE**")

    try:
        answer_code = random.randint(100000, 999999)
        sys.stdout.write(send_email(email, answer_code) + "\n")
    except Exception as e:
        sys.stdout.write(Fore.RED + "[EMAIL-ERROR#1] Error occurred while sending email, please check your email address validation and try again\n")
        return verify_email(None) # Return the result of the recursive call

    sys.stdout.write(Fore.GREEN + "[SUCCESS] " + Fore.WHITE + "A six-digit code was sent to your email, " + Fore.YELLOW + "remember to check your spam.\n")
    sys.stdout.write(Fore.WHITE + "[INFO] Type '-1' to re-enter email address, 'x' to cancel.\n")

    while True:
        code = input(Fore.WHITE + "[INPUT] Enter the 6-digit verification code: ")
        if code == "-1":
            sys.stdout.write(Fore.WHITE + "[INFO] Re-enter your email\n")
            return verify_email(email=None)  # Return the result of the recursive call
        elif code == str(answer_code):
            sys.stdout.write(Fore.GREEN + "[SUCCESS]" + Fore.YELLOW + " Authentication complete.\n" + Fore.WHITE)
            return email
        elif code.lower() == 'x':
            return
        else:
            sys.stdout.write(Fore.YELLOW + "[WARNING] Wrong code, try again!\n" + Fore.WHITE)

def manage_selected_package(package, email):
    """Manage the selected package."""
    package_name = package[1]
    package_version = package[2]
    package_description = package[3]  # Assuming package description is at index 3
    package_owner = package[4]  # Assuming package owner is at index 4

    o = True

    while True:
        if o == True:
            if os.name == 'nt':  # For Windows
                os.system('cls')
            else:  # For Unix/Linux/Mac
                os.system('clear')

        if o == False:
            break

        sys.stdout.write("******************************************************\n")
        sys.stdout.write(f"Managing {package_name} (Version {package_version}):\n")
        sys.stdout.write("[U] - Update: Use this option if you've updated this package and want to publish a new version of it.\n")
        sys.stdout.write("[I] - Information: Edit its information and ownership.\n")
        sys.stdout.write("[D] - Delete: Delete the package from the database as well as unpublish it.\n")
        sys.stdout.write("[C] - Copy: Get a copy of the zip of this package.\n")
        sys.stdout.write("[X] - Exit: Exit this menu.\n")
        option = input("Enter your option: ").strip().upper()
        
        if option == 'U':
            clean_console()
            sys.stdout.write("******************************************************\n")
            c = input("Enter path of your package: ")
            upload_package(c, email, check=False)
            delete_package(package_name, email)
            sys.stdout.write("Updating Completed")
            clean_console()
            
        elif option == 'I':
            while True:
                clean_console()
                sys.stdout.write("******************************************************\n")
                sys.stdout.write(f"Editing information for package {package_name}...\n")
                sys.stdout.write(f"[1] Package Name: {package_name}\n")
                sys.stdout.write(f"[2] Package Version: {package_version}\n")
                sys.stdout.write(f"[3] Package Description: {package_description}\n")
                sys.stdout.write(f"[4] Package Ownership: {package_owner}\n")
                sys.stdout.write("[S] Save: Save changes and exit.\n")
                sys.stdout.write("[X] Exit: Exit without saving.\n")
                
                edit_option = input("Select an option to edit or save: ").strip().upper()
                
                if edit_option == '1':
                    sys.stdout.write("******************************************************\n")
                    clean_console()
                    new_name = input("Enter new package name: ")
                    package_name = new_name  # Update the variable to reflect the change
                    clean_console()
                elif edit_option == '2':
                    sys.stdout.write("******************************************************\n")
                    clean_console()
                    new_version = input("Enter new package version: ")
                    package_version = new_version  # Update the variable to reflect the change
                    clean_console()
                elif edit_option == '3':
                    sys.stdout.write("******************************************************\n")
                    clean_console()
                    sys.stdout.write("[INFO] Type '_X_' to discard changes\n")
                    new_description = input("[INPUT] Enter new package brief description: ")
                    if new_description.lower() != '_x_':     
                        package_description = new_description  # Update the variable to reflect the change
                        clean_console()
                elif edit_option == '4':
                    sys.stdout.write("******************************************************\n")
                    clean_console()
                    new_owner = input("Enter new package owner: ")
                    package_owner = new_owner  # Update the variable to reflect the change
                    clean_console()
                elif edit_option == 'S' or edit_option == "s":
                    # Save changes to the database
                    if len(package_name) < 30 and len(package_version.split('.')) <= 4 and len(package_description[2]) < 300:
                        edit_package(package[1], package_name, package_version, package_description, package_owner)
                        clean_console()
                        sys.stdout.write(Fore.GREEN + "[SUCCESS] Saved changes.")
                        break  # Exit editing menu
                elif edit_option.lower() == 'x':
                    option = input("Are you sure? (y/n): ")
                    if option == "Y" or option == "y":
                        sys.stdout.write("Exiting without saving changes.\n")
                    break  # Exit editing menu
                else: 
                    sys.stdout.write("Invalid option. Please select a valid option.\n")
        
        elif option == 'D':
            confirm = input("Are you sure you want to delete this package? (Y/N): ")
            if confirm in ("y", "Y"):
                try:
                    link = search_package(package_name)[0][0]
                    upload.delete(link)
                    delete_package(package_name)
                except TypeError:
                    sys.stdout.write(Fore.RED + "[ERROR] Package does not exists.\nMaybe new data about that package was updated from database, type 'n' and retry.\n")
                    time.sleep(1)
                    clean_console()
                    return
                
                i = input("Continue to stay in this dialog? (Y/N): ")
                if i == "N" or i == "n":
                    o = True
                    break

        elif option == 'C':
            clean_console()
            sys.stdout.write("******************************************************\n")
            install_package(package_name)
            clean_console()
        elif option == 'X':
            sys.stdout.write("[INFO] Exiting management menu.\n")
            break
        else:
            sys.stdout.write(Fore.YELLOW + "[WARNING] Invalid option. Please enter a valid option.\n")
    
    return "quit"

def manage_uploads(email):
    """Manage uploaded packages by email."""
    email = verify_email(email)
    if email == "Canceled Operation.":
        return ""
    have_packages = search_owner(email)
    
    if not have_packages:
        return Fore.YELLOW + f"[WARNING] No packages found inside mail {email}. Either re-enter mail by typing 'manage-uploads <mail>' or upload a package by typing 'upload <dir>'. More info on http://use-nrm.us.to/faq/upload-no-package-mail"

    sys.stdout.write("******************************************************\n")
    sys.stdout.write(f"Owner: {email}\n")
    sys.stdout.write("Uploaded packages: \n")
    
    for index, package in enumerate(have_packages, start=1):
        package_name = package[1]  # The name of the package
        package_version = package[2]  # The version of the package
        sys.stdout.write(f"[{index}] {package_name}: {package_version}\n")
    
    sys.stdout.write(f"[X] Close\n")
    # Prompt user to select a package by number
    choice = input("Type the number of the desired package to manage it: ")
    
    while True:
        if choice == "x" or choice == "X":
            clean_console()
            return ""
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(have_packages):
                selected_package = have_packages[choice_index]
                stop = manage_selected_package(selected_package, email)
                if stop == "quit":
                    clean_console()
                    break
            else:
                sys.stdout.write("Invalid selection, try again.")
        except ValueError:
            return "Invalid input. Please enter a number."

def upload_template(dir):
    if dir == None:
        dir = os.getcwd()
    try:
        shutil.copytree(os.path.dirname(os.path.abspath(__file__))+"/template", dir)
        sys.stdout.write(Fore.GREEN + f"[SUCCESS] A folder of upload template has successfully copied to {dir} !")
    except NotADirectoryError:
        sys.stdout.write(Fore.RED + "[NOT-A-DIR-ERROR] Not a directory, please double check the sent path.\n" + Fore.WHITE + "More info at: " + Fore.BLUE + "http://use-nrm.us.to/faq/not-a-dir")
        return

def upload_package(dir, email, check=True):
    """Uploads a package after verifying ownership."""
    if check == True:
        email = verify_email(email)
        if email == "Canceled Operation.":
            return ""
    
    try:
        with open(os.path.join(dir, "details.nrm-package"), "r") as f:
            info = f.read().split('\n')  # Corrected to split by newline
    except FileNotFoundError:
        sys.stdout.write(Fore.RED + f"[UPLOAD-ERROR#1] Error, no 'details.nrm-package' found in dir {Fore.YELLOW + dir + Fore.RED}, try again. Run 'nrm upload-template' for upload template.\n")
        sys.stdout.write(Fore.WHITE + f"More info on " + Fore.BLUE + "http://use-nrm.us.to/faq/upload\n")
        exit()

    data = [line.split() for line in info]
    data[2] = ' '.join(data[2][1:])  # Clean up description

    package_name = data[0][1]  # Assuming the first line contains the package name
    if search_package(package_name):
        return Fore.YELLOW + f"[WARNING] Package with name '{Fore.YELLOW + package_name + Fore.YELLOW}' already exists. Please choose a different name."

    # Ensure the zip file is named correctly
    zip_file_path = os.path.join(dir, f"{package_name}.zip")  # Use package_name for the zip file
    zip_folder(dir, zip_file_path)  # Pass the correct zip file path
    download_link = upload.main(zip_file_path)  # Use the correct zip file path
    # Check of package_name, package_version, package_description length be4 upload
    if len(package_name) < 30 and len(data[1][1].split('.')) <= 4 and len(data[2]) < 300:
        insert_data(download_link, package_name, data[1][1], data[2], email)
        return Fore.GREEN + "[SUCCESS] Upload completed!"
    else:
        return Fore.RED + """[UPLOAD-ERROR#3] Rejected upload, make sure the 'details.nrm-package' has satisfied the requirements.
More info at """ + Fore.CYAN + "http://use-nrm.us.to/faq/rejected-upload"

def install_package(package):
    """Installs a package by retrieving its link from the database."""
    package_info = search_package(package)
    if not package_info:
        return Fore.RED + f"[INSTALL-ERROR#1] Package '{package}' not found in the database.\nSearch for packages in " + Fore.CYAN + "http://nrm-lib.us.to/"

    name = package
    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/installed._nrm_', 'r') as f:
        installed = f.read().splitlines()
        
    if name in installed:
        return Fore.YELLOW + f"[WARNING] Package '{name}' already installed. To update, type: 'update {name}'."

    package_link = package_info[0][0]
    sys.stdout.write(f"[INFO] Downloading package from {package_link}...\n")
    result = download_file(package, package_link)
    
    if result is None:
        return Fore.RED + f"[INSTALL-ERROR#1] Failed to install package '{package}'."
    else:
        with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/installed._nrm_', 'a') as f:
            f.write(name + '\n')
        
    return Fore.GREEN + f"[SUCCESS] Installation of package {name} is successfully completed."

def uninstall_package(package_name):
    """Uninstalls a package by removing it from the database and filesystem."""
    # First, check if the package is installed
    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/installed._nrm_', 'r') as f:
        installed = f.read().splitlines()

    if package_name not in installed:
        return Fore.YELLOW + f"[WARNING] Package '{package_name}' is not installed."

    option = input("Are you sure (y/n): ")
    if option == "Y" or option == "y":
        # Remove the package entry from the installed list
        installed.remove(package_name)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/installed._nrm_', 'w') as f:
            f.write('\n'.join(installed))

        # Remove the package files from the filesystem
        package_path = os.path.join(os.path.realpath(__file__) + "/packages/", package_name)  # Assuming packages are stored in a 'packages' directory
        if os.path.exists(package_path):
            try:
                shutil.rmtree(package_path)  # Use shutil.rmtree to remove the directory and its contents
                return Fore.GREEN + f"[SUCCESS] " + Fore.WHITE + f"Package '{package_name}' has been uninstalled successfully."
            except Exception as e:
                return Fore.RED + f"[UNINSTALL-ERROR#1] Error removing package files: {e}"
        else:
            return Fore.YELLOW + f"[WARNING] No files found for package '{package_name}'."
    else:
        return ""

def alias_options(option):
    """Manage alias options."""
    have_shortcuts = False
    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'r') as f:
        list_functions = f.read().strip().split('\n')
        if len(list_functions) >= 2:
            have_shortcuts = True

    def display_shortcuts(manage=True):
        """Display the available shortcuts."""
        if manage:
            clean_console()
        sys.stdout.write(Fore.WHITE+ "Available shortcuts:\n")
        for i in range(0, len(list_functions), 2):
            sys.stdout.write(f"[{round((i/2)+1)}] {list_functions[i]}: {list_functions[i+1]}\n")
        if manage:
            sys.stdout.write("[X] Cancel.\n")

    if option == '-show':
        if have_shortcuts:
            display_shortcuts(manage=False)
        else:
            sys.stdout.write(Fore.YELLOW + "[WARNING] No shortcuts available to .\n")
        return

    elif option == '-manage':
        if have_shortcuts:
            display_shortcuts()
        else:
            return Fore.YELLOW + "[WARNING] No shortcuts created.\nMore info at http://use-nrm.us.to/faq/alias"
        while have_shortcuts:
            if have_shortcuts:
                display_shortcuts()
            else:
                return Fore.YELLOW + "[WARNING] No shortcuts created.\nMore info at http://use-nrm.us.to/faq/alias"
            selection = input("Enter your selection: ")
            if selection.lower() == "x":
                break
            try:
                selection = int(selection) - 1
                if selection * 2 < len(list_functions):
                    current_shortcut = list_functions[selection * 2]
                    current_command = list_functions[selection * 2 + 1]

                    while True:
                        clean_console()
                        sys.stdout.write(Fore.WHITE + "Managing shortcut: {}\n".format(current_shortcut))
                        sys.stdout.write(f"[S] Edit shortcut's name (current: {current_shortcut})\n")
                        sys.stdout.write(f"[C] Edit command (current: {current_command})\n")
                        sys.stdout.write("[D] Delete this shortcut.\n")
                        sys.stdout.write("[A] Apply changes.\n")
                        sys.stdout.write("[X] Close.\n")
                        op = input("Enter your option: ")

                        if op.lower() == "d":
                            confirm = input("Are you sure you want to delete this shortcut? (y/n): ")
                            if confirm.lower() == "y":
                                del list_functions[selection * 2:selection * 2 + 2]
                                with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'w') as f:
                                    f.write('\n'.join(list_functions))
                                sys.stdout.write(Fore.GREEN + "[SUCCESS] Shortcut deleted.\n")
                                break  # Exit the inner loop to refresh the outer loop

                        elif op.lower() == "s":
                            new_name = input("Enter new shortcut name: ")
                            list_functions[selection * 2] = new_name
                            sys.stdout.write(Fore.GREEN + f"[SUCCESS] Shortcut name updated to '{new_name}'.\n")
                            current_shortcut = new_name  # Update the current shortcut variable
                            time.sleep(1)

                        elif op.lower() == "c":
                            new_command = input("Enter new command: ")
                            list_functions[selection * 2 + 1] = new_command
                            sys.stdout.write(Fore.GREEN + f"Command updated to '{new_command}'.\n")
                            current_command = new_command  # Update the current command variable

                        elif op.lower() == "a":
                            with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'w') as f:
                                f.write('\n'.join(list_functions))
                            sys.stdout.write(Fore.GREEN + "Changes applied.\n")
                            break  # Exit the inner loop to refresh the outer loop

                        elif op.lower() == "x":
                            sys.stdout.write("Exiting management menu.\n")
                            break

                        # Display updated values immediately
                        clean_console()
                        sys.stdout.write("Managing shortcut: {}\n".format(current_shortcut))
                        sys.stdout.write(f"[S] Edit shortcut's name (current: {current_shortcut})\n")
                        sys.stdout.write(f"[C] Edit command (current: {current_command})\n")
                        sys.stdout.write("[D] Delete this shortcut.\n")
                        sys.stdout.write("[A] Apply changes.\n")
                        sys.stdout.write("[X] Close.\n")

                else:
                    sys.stdout.write(Fore.RED + "[ERROR] Invalid selection. Try again.\n")
                    time.sleep(1)
            except (ValueError, IndexError):
                sys.stdout.write(Fore.RED + "[ERROR] Invalid input . Please enter a valid option.\n")
                time.sleep(1)

def alias(shortcut, command):
    """Creates a shortcut via 'key' and do command when pressed."""
    subcommands = ["-show", "-manage"]
    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'r') as f:
        list_functions = f.read().strip().split('\n')

    if shortcut in subcommands:
        alias_options(shortcut)
        return ""

    if shortcut in commands or shortcut in list_functions:
        return Fore.RED + f"[ERROR-ALIAS#3] '{shortcut}' is already used. Try again with a different name.\nOr run it by typing 'nrm {shortcut}'\nMore info at http://use-nrm.us.to/faq/error-alias3"

    if command is None:
        return Fore.RED + "[ERROR-ALIAS#2] No command assigned, try again.\nMore info at http://use-nrm.us.to/faq/error-alias2"

    with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/shortcuts._nrm_', 'a') as f:
        f.write(f"\n{shortcut}\n{command}")

    return Fore.GREEN + f"[SUCCESS] Successfully added command '{command}' with shortcut '{shortcut}'!"

def better_help(command):
    
    #commands = ["help", "credits", "upload", "version", "installed", "update", "install", "uninstall", "reinstall", "manage-packages", "manage-package","clean", "alias"]

    functions = {
        "version" : "Command version shows current NRM version.\nUsage: nrm version\nGet new releases at http://nrm.us.to",
        "credits" : "Shows the developers and contributors of NRM.\nUsage: nrm credits\nContribute at http://nrm.us.to/contribute",
        "alias" : "Creates shortcut for a command. Best used if command is long.\nUsage: nrm alias <shortcut/mode> <command>\nDetailed guide at http://use-nrm.us.to/faq/alias",
        "installed" : "Shows installed packages.\nUsage: nrm installed\nMore info at http://use-nrm.us.to/faq/installed",
        "upload" : "(Web version coming soon) Uploads a package from your computer to the database.\nUsage: nrm upload <package-directory> <email>\nHow to upload: http://use-nrm.us.to/faq/upload",
        "update" : "Update packages/NRM (if new version found).\nUsage: nrm update <nrm/package1> <package2> ...\nMore info at: http://use-nrm.us.to/faq/update",
        "install" : "Install packages (if multi packages were given) from NRM's database.\nUsage: nrm install <package1> <package2> ... \nYou can easily search for packages at http://nrm-lib.us.to",
        "reinstall" : "Reinstall packages (if multi packages were given). That package should be existed on your computer else it can't be performed.\nUsage: nrm reinstall <package1> <package2> ...",
        "uninstall" : "Uninstall packages (if multi packages were given). That package should be existed on your computer else it can't be performed.\nUsage: nrm uninstall <package1> <package2> ...",
        "manage-packages" : "(Web version coming soon) A place to manage your packages.\nUsage: nrm manage-packages <email>\nMore info can be found at: http://use-nrm.us.to/faq/manage-package",
        "manage-package" : "(Web version coming soon) A place to manage your packages.\nUsage: nrm manage-packages <email>\nMore info can be found at: http://use-nrm.us.to/faq/manage-package",
        "clean" : "Clears out the terminal.\nUsage: nrm clean\nMore info can be found at: http://use-nrm.us.to/faq/clean",
        "exit" : "Exits runtime (only works when using nrm runtime).\nUsage: (only in nrm runtime) exit\nMore info: " + Fore.BLUE + "http://use-nrm.us.to/faq/exit"
    }

    if command in functions:
        return f"""--------------------------------------------------------------
{functions[command]}
--------------------------------------------------------------"""
    
    return None
    
def do_alias(shortcut, command):
    sys.stdout.write(Fore.CYAN + f"[ALIAS] Executing shortcut command '{shortcut}'...\n" + Fore.WHITE)
    try:
        result = subprocess.run(['nrm', shortcuts[shortcuts.index(command)]], capture_output=True, text=True)
        sys.stdout.write(result.stdout)
        return
    except:
        raise Fore.RED + f"[ALIAS-ERROR#1] Error occured while running shortcut command {shortcut}\nMore info at http://use-nrm.us.to/faq/aliaserror1"

def do_func(mode, arguments):
    """Execute commands based on user input."""
    if mode == "version":
        return "Current version: NRM - v0.0.1 Beta"
    
    elif mode == "credits":
        return "NRM: Made by @Lam and @iaminfinityiq"
    
    elif mode == "installed":
        # do installed
        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + '/nrmdata/installed._nrm_', 'r') as f:
                installed = f.readlines()
            if not installed:
                return Fore.YELLOW + "[NOTICE] No packages installed right now, how about installing one?"
            return "Installed packages: " + ", ".join(pkg.strip() for pkg in installed)
        except FileNotFoundError:
            return "[NOTICE] No packages have been installed yet.\n"
        
    elif mode == "install":
        # do install
        if not arguments:
            return "Usage: nrm install <package1> <package2> ...\nMore info by typing 'nrm help install'."
        return "\n".join(install_package(arg) for arg in arguments)
    
    elif mode == "uninstall":
        # do uninstall
        if len(arguments) == 0:
            return Fore.YELLOW + "[WARNING] Please specify the package name to uninstall.\n" + Fore.WHITE + "Usage: nrm uninstall <package1> <package2> ..."
        return uninstall_package(arguments[0])  # Uninstall the specified package
    
    elif mode == "upload":
        # do upload
        try:
            return upload_package(arguments[0], os.getcwd() + arguments[1] if len(arguments) > 1 else None)
        except IndexError:
            return Fore.RED + "[FILE-ERROR#3b] Directory argument is missing.\nMore information at http://use-nrm.us.to/faq/fileerror3b\n"
        
    elif mode == "upload-template":
        # do upload-template
        try:
            return upload_template(arguments[0])
        except IndexError:
            return upload_template(None)
        
    elif mode == "manage-packages" or mode == "manage-package":
        return manage_uploads(arguments[0] if arguments else None)
    elif mode == "clean":
        clean_console()
    elif mode == "reinstall":
        for i in range(len(arguments)):
            reinstall(arguments[i])
    elif mode == "alias":
        try:
            shortcut = arguments[0]
            command = ' '.join(arguments[1:])
            return alias(shortcut, command)  # Ensure alias returns a string
        except IndexError:
            return "[TIP] Usage: nrm alias <shortcut> <command>"
    elif mode == "help":
        try:
            command = arguments[0]
            if command == '' or command == '-all':
                sys.stdout.write(help_text + "\n")
                return
            if better_help(command) != None:
                sys.stdout.write("--------------------------------------------------------------\n")
                sys.stdout.write(f"Prompt: {command}\n")
                return better_help(command)
            else:
                return Fore.RED + "[ERROR-HELP] Invalid command, find the list of commands at " + Fore.CYAN + "http://nrm-lib.us.to/commands"
        except IndexError:
            return help_text

def do_sub(command, arg=None, source=False):
    """Do subcommands"""
    if command == "-runtime" and source == False:
        return main()

def main():
    command_history = []
    sys.stdout.write("[INFO] Entered nrm runtime.\n")
    while True:
        try:
            nrm = input(Fore.WHITE + "nrm> ")
            try:
                nrm.split('.')[1]
                run_file = nrm
            except IndexError:
                run_file = None
            # Add the command to history
            command_history.append(nrm)
            readline.add_history(nrm)  # Add to readline history

            args = nrm.split()
            if not args:
                sys.stdout.write(help_text + "\n")
                continue

            nrm_command = args[0]
            del args[0]

            if nrm_command == "exit":
                break
            
            elif "nrm" in nrm_command:
                if nrm_command.count('.nrm') != 0:
                    try:
                        from interpreter import execute_code
                        execute_code(nrm)
                    except FileNotFoundError:
                        sys.stdout.write(Fore.RED + f"[FILE-ERROR#1] File not found for '{sys.argv[1]}' in dir {os.getcwd()}\nMore info at http://use-nrm.us.to/faq/fileerror1")
                        exit()
                else:
                    sys.stdout.write(Fore.YELLOW + f"[WARNING] Please type 'exit' to include 'nrm' in the start or start typing without 'nrm' in start.\n")

            elif nrm_command in shortcuts:
                if shortcuts.index(nrm_command) % 2 == 0:
                    do_alias(shortcut=shortcuts[shortcuts.index(nrm_command)], command=shortcuts[shortcuts.index(nrm_command)+1])
                elif nrm_command.count('.nrm') == 0:
                    sys.stdout.write(Fore.RED + f"[TERMINAL-ERROR#1] Unknown command '{nrm_command}'.\n" + Fore.CYAN + "More info at http://use-nrm.us.to/faq/terinalmerror1\n")
                else:
                    # run file functionality
                    try:
                        from interpreter import execute_code
                        execute_code(nrm)
                    except FileNotFoundError:
                        sys.stdout.write(Fore.RED + f"[FILE-ERROR#1] File not found for '{sys.argv[1]}' in dir {os.getcwd()}\nMore info at http://use-nrm.us.to/faq/fileerror1\n")

            elif nrm_command in subcommands:
                if args:
                    do_sub(nrm_command, arg=args)
                do_sub(nrm_command)

            elif nrm_command in commands:
                s = do_func(nrm_command, args)
                if s:
                    sys.stdout.write(s + "\n")

            elif nrm_command.count('.nrm') == 0:
                sys.stdout.write(Fore.RED + f"[TERMINAL-ERROR#1] Unknown command '{nrm_command}'.\n" + Fore.CYAN + "More info at http://use-nrm.us.to/faq/terinalmerror1\n")
                
            elif nrm != None:
                # run file functionality
                try:
                    from interpreter import execute_code
                    execute_code(nrm)
                except FileNotFoundError:
                    sys.stdout.write(Fore.RED + f"[FILE-ERROR#1] File not found for '{sys.argv[1]}' in dir {os.getcwd()}\nMore info at http://use-nrm.us.to/faq/fileerror1\n")

        except KeyboardInterrupt:
            sys.stdout.write("\n[NOTICE] Force Quitting terminal...\n")
            sys.exit(1)

def prase():
    try:
        args = sys.argv[1:]

        if not args:
            sys.stdout.write(help_text + "\n")

        nrm_command = args[0]
        del args[0]

        if nrm_command in commands:
            s = do_func(nrm_command, args)
            if s:
                sys.stdout.write(s + "\n")

        elif nrm_command in subcommands:
            do_sub(nrm_command)

        elif nrm_command in shortcuts:
            if shortcuts.index(nrm_command) % 2 == 0:
                    do_alias(shortcut=shortcuts[shortcuts.index(nrm_command)], command=shortcuts[shortcuts.index(nrm_command)+1])
            elif nrm_command.count('.nrm') == 0:
                sys.stdout.write(Fore.RED + f"[TERMINAL-ERROR#1] Unknown command '{nrm_command}'.\n" + Fore.CYAN + "More info at http://use-nrm.us.to/faq/terinalmerror1\n")
            else:
                # run file functionality
                try:
                    from interpreter import execute_code
                    execute_code(nrm_command)
                except FileNotFoundError:
                    sys.stdout.write(Fore.RED + f"[FILE-ERROR#1] File not found for '{sys.argv[1]}' in dir {os.getcwd()}\nMore info at http://use-nrm.us.to/faq/fileerror1\n")

        elif nrm_command.count('.nrm') == 0:
            sys.stdout.write(Fore.RED + f"[TERMINAL-ERROR#1] Unknown command '{nrm_command}'.\n" + Fore.WHITE + "More info at " + Fore.BLUE + "http://use-nrm.us.to/faq/terminalmerror1\n")
            return

    except KeyboardInterrupt:
        sys.stdout.write("\n[INFO] Force Quitting terminal...\n")
        sys.exit(1)

if __name__ == '__main__':
    try:
        try:
            sys.argv[1].split('.')[1]
            run_file = sys.argv[1].split('.')
            if run_file[1].lower() == "nrm":
                # run file functionality
                try:
                    from interpreter import execute_code
                    execute_code(sys.argv[1])
                except FileNotFoundError:
                    sys.stdout.write(Fore.RED + f"[FILE-ERROR#1] File not found for '{Fore.YELLOW + sys.argv[1] + Fore.RED}' in dir '{Fore.YELLOW + os.getcwd() + Fore.RED}'\n" + Fore.WHITE + "More info at " + Fore.BLUE + "http://use-nrm.us.to/faq/fileerror1\n")
                    exit(1)
            else:
                sys.stdout.write(Fore.RED + f"[FILE-ERROR#2] Enter a valid extension, got '{Fore.YELLOW + run_file[1] + Fore.RED}'.\n" + Fore.WHITE + "More info at " + Fore.BLUE + "http://use-nrm.us.to/faq/fileerror2\n")
                exit(1)
        except IndexError:
            sys.argv[1:]
            prase()
    except IndexError:
        try:
            sys.stdout.write("To enter nrm's runtime: type 'nrm -runtime'"+"\n")
            sys.stdout.write("--------------------------------------------------------------")
            exit()
        except ValueError:
            exit()

import frappe
import subprocess
import sys

PACKAGE_LIST = [
    "playsound",
    "gTTS",
    "opencv-python",
    "python-escpos",
    "pyusb",
    "pyserial",
    "swig",
    "pyscard",
    "pyscard",
    "smartcard",
    
    
]

@frappe.whitelist()
def before_install():
    install_system_packages()
    install_python_packages()
    

@frappe.whitelist()
def install_python_packages():
    try:
        for package in PACKAGE_LIST:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")


@frappe.whitelist()
def install_system_packages():
    try:
        # Update package list
        subprocess.check_call(['sudo', 'apt-get', 'update'])

        # Install swig
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'swig'])

        # Install pcscd and libpcsclite-dev
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'pcscd', 'libpcsclite-dev'])

        # Install opensc-pkcs11, pcscd, sssd, libpam-sss
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'opensc-pkcs11', 'pcscd', 'sssd', 'libpam-sss'])

        # Install gnutls-bin
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'gnutls-bin'])

        # Install opensc
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'opensc'])

        # Remove the pn533_usb module
        subprocess.check_call(['sudo', 'rmmod', 'pn533_usb'])

        #install mpg321
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'mpg321'])

        

        print("All system packages installed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Failed to install system packages: {e}")
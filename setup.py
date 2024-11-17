import os
import subprocess
import sys

def run_command(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def setup_environment():
    print("Setting up the environment...")
    
    # Create necessary directories
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Install basic requirements
    requirements = [
        "flask",
        "torch",
        "transformers>=4.33.2",
        "gtts",
        "pillow",
        "nltk",
        "sacremoses",
        "pandas",
        "regex",
        "mock",
        "mosestokenizer",
        "bitsandbytes",
        "scipy",
        "accelerate",
        "datasets",
        "sentencepiece"
    ]
    
    print("Installing basic requirements...")
    for req in requirements:
        print(f"Installing {req}...")
        code, out, err = run_command(f"pip install {req}")
        if code != 0:
            print(f"Error installing {req}: {err}")
            return False

    # Download NLTK data
    print("Downloading NLTK data...")
    import nltk
    nltk.download('punkt')

    # Clone repositories
    print("Cloning IndicTrans2...")
    if not os.path.exists("IndicTrans2"):
        code, out, err = run_command("git clone https://github.com/AI4Bharat/IndicTrans2.git")
        if code != 0:
            print(f"Error cloning IndicTrans2: {err}")
            return False

    print("Cloning IndicTransToolkit...")
    if not os.path.exists("IndicTransToolkit"):
        code, out, err = run_command("git clone https://github.com/VarunGumma/IndicTransToolkit.git")
        if code != 0:
            print(f"Error cloning IndicTransToolkit: {err}")
            return False

    # Install IndicTransToolkit
    print("Installing IndicTransToolkit...")
    os.chdir("IndicTransToolkit")
    code, out, err = run_command("pip install --editable .")
    os.chdir("..")
    if code != 0:
        print(f"Error installing IndicTransToolkit: {err}")
        return False

    print("Setup completed successfully!")
    return True

if __name__ == "__main__":
    success = setup_environment()
    if not success:
        print("Setup failed!")
        sys.exit(1)
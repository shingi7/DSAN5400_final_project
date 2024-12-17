import subprocess
import sys

def run_command(command):
    """Run a shell command and handle errors."""
    try:
        subprocess.check_call(command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print(f"Command succeeded: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error while running: {command}\n{e}")

def main():
    # Commands to run
    commands = [
        "git -C ColBERT/ pull || git clone https://github.com/stanford-futuredata/ColBERT.git",
        "wget 'https://downloads.cs.stanford.edu/nlp/data/colbert/colbertv2/colbertv2.0.tar.gz'",
        "mkdir -p checkpoints",  # Create the 'checkpoints' directory if it doesn't exist
        "!tar -xvzf colbertv2.0.tar.gz -C checkpoints",
        "pip install -U pip",
        "pip install fsspec==2024.9.0",
        "pip install -e ColBERT/['faiss-gpu','torch'] > /dev/null 2>&1",
        "pip install --upgrade torch torchvision torchaudio"
    ]

    # Execute each command
    for command in commands:
        run_command(command)

if __name__ == "__main__":
    main()

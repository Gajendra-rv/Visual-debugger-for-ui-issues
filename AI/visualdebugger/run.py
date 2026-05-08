"""Application entry point."""
import os
import sys
import subprocess

def activate_venv_and_run():
    """Ensure the script runs within the virtual environment."""
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
    venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')
    
    if os.path.abspath(sys.executable) != os.path.abspath(venv_python) and os.path.exists(venv_python):
        print(f"[Info] Re-launching application using virtual environment...")
        sys.exit(subprocess.call([venv_python] + sys.argv))

activate_venv_and_run()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("instance", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(os.path.join("app", "static", "uploads"), exist_ok=True)
    os.makedirs(os.path.join("app", "static", "heatmaps"), exist_ok=True)
    os.makedirs(os.path.join("app", "static", "reports"), exist_ok=True)
    os.makedirs(os.path.join("app", "static", "models"), exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)

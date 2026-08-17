import os
import subprocess

def start_celery_beat():
    print("Starting Celery Beat Scheduler...")
    # Get the absolute path to the backend directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    
    try:
        # Run the celery command inside the backend directory
        subprocess.run(['celery', '-A', 'app.celery', 'beat', '--loglevel=info'], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nStopping Celery Beat Scheduler...")
    except FileNotFoundError:
        print("\nERROR: 'celery' command not found. Make sure your virtual environment is active!")

if __name__ == "__main__":
    start_celery_beat()

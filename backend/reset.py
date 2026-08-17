"""Database reset and full cache cleanup"""
import os
import sys
import shutil
import glob
import redis

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app import create_app
from extensions import db
from models.user import User

def clean_caches_and_exports():
    print("\n--- Cleaning Caches & Background Files ---")
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # pycache__ folders
    pycache_count = 0
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)
            pycache_count += 1
            dirs.remove('__pycache__') # don't traverse into it
    print(f"Deleted {pycache_count} __pycache__ directories.")

    # instance folder
    instance_dir = os.path.join(base_dir, 'backend', 'instance')
    if os.path.exists(instance_dir):
        try:
            shutil.rmtree(instance_dir)
            print("Deleted 'instance' folder (SQLite database wiped).")
        except PermissionError:
            print("Warning: Could not delete 'instance' folder completely. The file might be open in another terminal. Tables will still be dropped.")

    # Celery schedule files
    celery_files = glob.glob(os.path.join(base_dir, 'celerybeat-schedule*'))
    for f in celery_files:
        try:
            os.remove(f)
            print(f"Deleted Celery file: {os.path.basename(f)}")
        except Exception:
            pass

    # Exports folder
    exports_dir = os.path.join(base_dir, 'backend', 'exports')
    if os.path.exists(exports_dir):
        export_count = 0
        for filename in os.listdir(exports_dir):
            file_path = os.path.join(exports_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                export_count += 1
        print(f"Cleared {export_count} exported files (PDFs/CSVs).")
    else:
        os.makedirs(exports_dir) # create it if it didn't exist
    
    # Flush Redis
    try:
        r = redis.Redis(host='localhost', port=6379)
        if r.ping():
            r.flushall() # This deletes everything inside Redis!
            print("Successfully flushed all data from Redis.")
    except redis.exceptions.ConnectionError:
        print("Redis is not running. Skipped Redis flush.")

def reset_database():
    print("Resetting  Database")
    app = create_app()
    with app.app_context():
        # delete all  table with data
        db.drop_all()
        # create empty table
        db.create_all()
        
        # admin seed
        admin = User(
            username='admin',
            email='admin@ppa.com',
            role='admin',
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Database reset complete. Admin account recreated (admin / admin123).")

if __name__ == '__main__':
    print("This will completely wipe your SQLite database, clear all Python caches, flush Redis, delete Celery schedules, and remove all exported PDFs/CSVs!")
    confirm = input("Type 'yes' to proceed with the hard reset: ")
    if confirm.lower() == 'yes':
        clean_caches_and_exports()
        reset_database()
        print("All systems  reset ")
    else:
        print("Aborted.")

import redis
import subprocess
import time
import sys

def check_redis():
    try:
        # Connect to local Redis instance
        r = redis.Redis(host='localhost', port=6379)
        # Send PING command
        if r.ping():
            print("Redis is running already (PONG)")
            return True
    except redis.exceptions.ConnectionError:
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    return False

if __name__ == "__main__":
    if check_redis():
        sys.exit(0)
    
    print("Redis is not running. Attempting to start Redis server...")
    
    try:
        # This will open a new console window on Windows and run redis-server
        # Make sure redis-server is in your environment variables/PATH
        subprocess.Popen(['redis-server'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Wait a moment for it to boot up
        print("Waiting for Redis to start...")
        time.sleep(2)
        
        # Check again
        if check_redis():
            print("Successfully started Redis server!")
        else:
            print("Could not verify Redis started. Please check if redis-server is installed correctly.")
            
    except FileNotFoundError:
        print("\nERROR: 'redis-server' command not found!")
        print("Please ensure Redis is installed on Windows and added to your system PATH.")
        print("If you are using WSL (Windows Subsystem for Linux), you may need to run 'wsl redis-server' manually.")

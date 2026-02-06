import os
import shutil
import json
import sys

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Assuming mirror is at ../mirror relative to github-publisher
MIRROR_SITES_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'mirror', 'sites'))
PUBLISHER_SITES_DIR = os.path.join(CURRENT_DIR, 'sites')

def sync_sites():
    print(f"Syncing sites from {MIRROR_SITES_DIR} to {PUBLISHER_SITES_DIR}...")
    
    if not os.path.exists(MIRROR_SITES_DIR):
        print(f"Error: Mirror sites directory not found at {MIRROR_SITES_DIR}")
        return False

    if not os.path.exists(PUBLISHER_SITES_DIR):
        os.makedirs(PUBLISHER_SITES_DIR)

    # Get list of files
    mirror_files = [f for f in os.listdir(MIRROR_SITES_DIR) if f.endswith('.json')]
    
    count = 0
    for filename in mirror_files:
        src = os.path.join(MIRROR_SITES_DIR, filename)
        dst = os.path.join(PUBLISHER_SITES_DIR, filename)
        
        # Simple copy
        shutil.copy2(src, dst)
        print(f"Copied: {filename}")
        count += 1
        
    print(f"Successfully synced {count} files.")
    return True

if __name__ == "__main__":
    sync_sites()

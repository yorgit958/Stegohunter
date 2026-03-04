import os
import sys
import subprocess

with open('requirements-db.txt', 'w') as f:
    f.write('supabase>=2.3.0\n')

print("Installing python supabase client for testing...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-db.txt"])
print("Ready to integrate.")

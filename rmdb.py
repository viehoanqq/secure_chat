# reset_db.py
import os, shutil
print("Deleting DB and keys...")
os.path.exists("instance/app.db") and os.remove("instance/app.db")
os.path.exists("keys") and shutil.rmtree("keys")
print("Reset complete!")
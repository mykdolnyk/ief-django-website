"""A Python script for initial setup of the application in Docker."""
import subprocess

# Migrate the DB
migrate = subprocess.run(["python", "manage.py", "migrate"], capture_output=True, text=True)
if migrate.returncode != 0:
    raise Exception(f"Migration command failed with exit code {migrate.returncode}. Error output:\n{migrate.stderr}")
else:
    print(migrate.stdout)

# Load the AwardTypes
awardtypes_load = subprocess.run(["python", "manage.py", "loaddata", "dumps/awardtypes_data.json"], capture_output=True, text=True)
if awardtypes_load.returncode != 0:
    raise Exception(f"Dump loading command failed with exit code {awardtypes_load.returncode}. Error output:\n{awardtypes_load.stderr}")
else:
    print(awardtypes_load.stdout)
    
# Load the blog Sections
blogsection_load = subprocess.run(["python", "manage.py", "loaddata", "dumps/blogsections_data.json"], capture_output=True, text=True)
if blogsection_load.returncode != 0:
    raise Exception(f"Dump loading command failed with exit code {blogsection_load.returncode}. Error output:\n{blogsection_load.stderr}")
else:
    print(blogsection_load.stdout)

# Load Celery Beat tasks
celery_beat_load = subprocess.run(["python", "manage.py", "loaddata", "dumps/celery_beat_data.json"], capture_output=True, text=True)
if celery_beat_load.returncode != 0:
    raise Exception(f"Dump loading command failed with exit code {celery_beat_load.returncode}. Error output:\n{celery_beat_load.stderr}")
else:
    print(celery_beat_load.stdout)

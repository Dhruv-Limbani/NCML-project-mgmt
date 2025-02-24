# fastapi
from fastapi import HTTPException, status

# models and schemas
from models.project import Project

# os and environment
import os, shutil
from dotenv import load_dotenv
load_dotenv()

STORAGE_LOC = os.getenv("STORAGE_LOC")

def check_db_connection(conn):
    try:
        conn.server_info()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database not live")

def is_authorized(project: Project, email: str):
    if project.email != email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

def read_file(loc):
    path = STORAGE_LOC + loc
    with open(path, 'r') as file:
        file_content = file.read()
    return file_content

def write_file(loc, content):
    path = STORAGE_LOC + loc
    with open(path, 'w') as file:
        file.write(content)
    return

def create_files(project: Project, email: str):
    base_dir = os.path.join(STORAGE_LOC, email, project.name)
    os.makedirs(base_dir, exist_ok=True)

    notes_loc = os.path.join(email, project.name, "notes.txt")
    logs_loc = os.path.join(email, project.name, "logs.txt")

    write_file(notes_loc, project.notes)
    write_file(logs_loc, project.logs)

    project.notes = notes_loc
    project.logs = logs_loc

    return project

def update_files(project: Project, name: str, email: str):
    base_dir = os.path.join(STORAGE_LOC, email, project.name)
    os.makedirs(base_dir, exist_ok=True)

    if project.name != name:
        path = os.path.join(STORAGE_LOC, email, name)
        shutil.rmtree(path, ignore_errors=True)

    notes_loc = os.path.join(email, project.name, "notes.txt")
    logs_loc = os.path.join(email, project.name, "logs.txt")

    write_file(notes_loc, project.notes)
    write_file(logs_loc, project.logs)

    project.notes = notes_loc
    project.logs = logs_loc

    return project

def delete_files(name: str, email: str):
    path = os.path.join(STORAGE_LOC, email, name)
    shutil.rmtree(path, ignore_errors=True)



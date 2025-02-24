from utils.utils import read_file

def projectEntity(item) -> dict:
    return {
        "name":item["name"],
        "email":item["email"],
        "notes":read_file(item["notes"]),
        "logs":read_file(item["logs"])
    }

def projectsEntity(items) -> list:
    return [projectEntity(item) for item in items]
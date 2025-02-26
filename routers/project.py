# fastapi
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

# db
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from db_service.mongodb_service import conn

# models and schemas
from models.project import Project
from schemas.project import projectEntity, projectsEntity

# utilities
from utils.utils import check_db_connection, is_authorized, create_files, update_files, delete_files


project_router = APIRouter()

@project_router.get('/all', tags=['project'],
    responses={
        200: {"description": "Projects Retrieved Successfully!"},
        400: {"description": "Bad Request!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint retrieves all the projects of the given user."
)
async def get_projects(email: str):

    check_db_connection(conn)

    projects =  conn.local.projects.find({"email": email})

    if projects is None:
        raise HTTPException(status_code=400, detail="Projects not found!")

    return projectsEntity(projects)

@project_router.get('/', tags=['project'],
    responses={
        200: {"description": "Project Retrieval Successful!"},
        400: {"description": "Bad Request!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint retrieves a project with the given details."
)
async def get_project(name: str, email: str):

    check_db_connection(conn)

    project =  conn.local.projects.find_one({"email": email, "name": name})

    if project is None:
        raise HTTPException(status_code=400, detail="Project not found!")

    return projectEntity(project)

@project_router.post("/", tags=["project"],
    responses = {
        200: {"description": "Project Creation Successful!"},
        400: {"description": "Bad Request!"},
        500: {"description": "Database Not Live!"}
    },
    description = "This endpoint creates a new project with the given details."
)
async def create_project(project: Project, email: str):

    is_authorized(project, email)

    check_db_connection(conn)

    try:
        if conn.local.projects.find_one({"email": email,"name": project.name}):
            raise HTTPException(status_code=400, detail="Project with this name already exists!")

        project = create_files(project, email)

        conn.local.projects.insert_one(dict(project))
        return JSONResponse({"message": "Project creation successful!"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@project_router.put("/", tags=["project"],
    responses={
        200: {"description": "Project modification successful!"},
        400: {"description": "Bad Request!"},
        404: {"description": "Project not found!"},
        409: {"description": "Name already in use!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint modifies the details of an existing project."
)
async def update_project(new: Project, name: str, email: str):

    is_authorized(new, email)

    check_db_connection(conn)

    if conn.local.projects.find_one({"email": email, "name": name}) is None:
        raise HTTPException(status_code=400, detail="Project does not exists!")

    try:
        new = update_files(new, name, email)
        update_data = {k: v for k, v in dict(new).items() if k not in ["_id", "email"]}
        updated_project = conn.local.projects.find_one_and_update(
            {"email": email,"name": name},
            {'$set': update_data},
            return_document=ReturnDocument.AFTER  # Return the updated user
        )

        if not updated_project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


        return JSONResponse({"message": "Project updated successfully", "updated details": projectEntity(updated_project)}, status_code=200)

    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A project with this name already exists under this email")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@project_router.delete("/", tags=["project"],
    responses={
        200: {"description": "Project deletion successful!"},
        404: {"description": "Project not found!"},
        500: {"description": "Database Not Live!"}
    },
    description="This endpoint deletes a project by it's user and name"
)
async def delete_project(name: str, email: str):

    check_db_connection(conn)

    deleted_project = conn.local.projects.find_one_and_delete({"email": email, "name": name})

    if not deleted_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    delete_files(name, email)

    return {"message": "Project deleted successfully"}
# fastapi
from fastapi import APIRouter

# db
from db_service.mongodb_service import conn

# models and schemas
from schemas.project import projectsEntity

# utilities
from utils.utils import check_db_connection

health_router = APIRouter()

@health_router.get("/", tags=["health"], response_model=dict,
    responses={
       500: {"description": "Database Not Live!"}
    },
   description="Health check for the database."
)
async def health_check():
    """Checks database connection and returns a list of users if the DB is live."""
    check_db_connection(conn)
    projects = list(conn.local.projects.find())

    return {"status": "Database is live", "projects": projectsEntity(projects)}

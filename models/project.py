from pydantic import BaseModel

class Project(BaseModel):
    name: str
    email: str
    notes: str
    logs: str



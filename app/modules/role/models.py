from pydantic import BaseModel

class RoleBaseModel(BaseModel):
    name: str
    description: str

class RoleParentModel(RoleBaseModel):
    parent_id: int

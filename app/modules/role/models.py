from pydantic import BaseModel

class RoleBaseModel(BaseModel):
    id: int
    name: str
    description: str
    access: str

class RoleParentModel(RoleBaseModel):
    parent_id: int

class RoleInDBModel(RoleBaseModel):
    is_default: bool
    is_admin: bool
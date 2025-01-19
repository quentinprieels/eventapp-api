from sqlalchemy import Column, Integer, String, Boolean

from app.db.base import GlobalBase

class RoleSchema(GlobalBase):
    """
    Define the Role schema
    A role is a set of permissions that can be assigned to a user.
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    categorie = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True)
    default_global = Column(Boolean, nullable=False)
    default_event = Column(Boolean, nullable=False)
    default_admin = Column(Boolean, nullable=False)
    parent_id = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    access = Column(String, nullable=True)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Role {self.name}>"
    
    def __eq__(self, other):
        return self.name == other.name
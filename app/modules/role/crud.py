from sqlalchemy.orm import Session

from app.modules.role.schemas import RoleSchema
from app.modules.role.models import RoleBaseModel
from app.exceptions import InvalidRole

# Get the default roles
def get_default_global_role(db: Session) -> RoleBaseModel:
    db_role = db.query(RoleSchema).filter(RoleSchema.default_global).first()
    return RoleBaseModel(**db_role.__dict__)

def get_default_event_role(db: Session) -> RoleBaseModel:
    db_role = db.query(RoleSchema).filter(RoleSchema.default_event).first()
    return RoleBaseModel(**db_role.__dict__)

def get_default_admin_role(db: Session) -> RoleBaseModel:
    db_role = db.query(RoleSchema).filter(RoleSchema.default_admin).first()
    return RoleBaseModel(**db_role.__dict__)

# Get list of roles
def get_global_role_by_name(db: Session, role_name: str) -> RoleBaseModel:
    db_role = db.query(RoleSchema).filter(RoleSchema.name == role_name).first()
    if not db_role:
        raise InvalidRole()
    return RoleBaseModel(**db_role.__dict__)

# Resolve the role hierarchy for JWT token creation
def get_user_global_roles_jwt_format(db: Session, user_global_role: str) -> list[str]:
    """
    Get the list of roles in the JWT format that the user has by resolving the role hierarchy.
    Return the list of the roles in format "globla:<role_name>" with all the global role that the user has.
    """
    # Get the user global role
    db_role = db.query(RoleSchema).filter(RoleSchema.name == user_global_role).first()
    user_roles = [f"global:{db_role.name}"]
    
    # Get all the childs and subchilds of the user global role
    roles_stack = [db_role]
    while roles_stack:
        current_role = roles_stack.pop()
        children_roles = db.query(RoleSchema).filter(RoleSchema.parent_id == current_role.id, RoleSchema.categorie == "global").all()
        if children_roles:
            roles_stack.extend(children_roles)
            user_roles.extend([f"global:{child_role.name}" for child_role in children_roles])
    return user_roles
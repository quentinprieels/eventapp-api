from sqlalchemy.orm import Session

from app.modules.role.schemas import GlobalRoleSchema, EventRoleSchema
from app.modules.role.models import RoleBaseModel, RoleInDBModel
from app.exceptions import InvalidRole

# Get the default roles
def get_default_global_role(db: Session) -> RoleBaseModel:
    db_role = db.query(GlobalRoleSchema).filter(GlobalRoleSchema.is_default).first()
    return RoleBaseModel(**db_role.__dict__)

def get_default_event_role(db: Session) -> RoleBaseModel:
    db_role = db.query(EventRoleSchema).filter(EventRoleSchema.is_default).first()
    return RoleBaseModel(**db_role.__dict__)

def get_default_admin_role(db: Session) -> RoleBaseModel:
    db_role = db.query(GlobalRoleSchema).filter(GlobalRoleSchema.is_admin).first()
    return RoleBaseModel(**db_role.__dict__)

# Get list of roles
def get_global_role_by_name(db: Session, role_name: str) -> RoleInDBModel:
    db_role = db.query(GlobalRoleSchema).filter(GlobalRoleSchema.name == role_name).first()
    if not db_role:
        raise InvalidRole()
    return RoleInDBModel(**db_role.__dict__)

# Resolve the role hierarchy for JWT token creation
def get_user_global_roles_jwt_format(db: Session, user_global_role_id: str) -> list[str]:
    """
    Get the list of roles in the JWT format that the user has by resolving the role hierarchy.
    Return the list of the roles in format "globla:<role_name>" with all the global role that the user has.
    """
    # Get the user global role
    db_role = db.query(GlobalRoleSchema).filter(GlobalRoleSchema.id == user_global_role_id).first()
    user_roles = [f"global:{db_role.name}"]
    
    # Get all the childs and subchilds of the user global role
    roles_stack = [db_role]
    while roles_stack:
        current_role = roles_stack.pop()
        children_roles = db.query(GlobalRoleSchema).filter(GlobalRoleSchema.parent_name == current_role.name).all()
        if children_roles:
            roles_stack.extend(children_roles)
            user_roles.extend([f"global:{child_role.name}" for child_role in children_roles])
    return user_roles
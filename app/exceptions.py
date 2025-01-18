from fastapi import HTTPException, status
from app.core.config import settings

class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="No user found with this email.")
        
class InvalidPassword(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
        
class CredentialsException(HTTPException):
    def __init__(self, authenticate: str = "Bearer", detail: str = None):
        detail_str = "Could not validate credentials"
        if detail:
            detail_str += f": {detail}"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail_str, headers={"WWW-Authenticate": authenticate})

class RoleNotAssignable(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
        
class InvalidImage(HTTPException):
    def __init__(self, detail: str = ""):
        detail_str = f"Invalid image file. {detail}"
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail_str)

class ImageNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
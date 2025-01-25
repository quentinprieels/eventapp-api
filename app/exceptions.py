from fastapi import HTTPException, status

# User exceptions
class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="No user found with this email.")


# Credentials exceptions      
class InvalidPassword(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
        
class CredentialsException(HTTPException):
    def __init__(self, authenticate: str = "Bearer", detail: str = None, status_code: int = status.HTTP_401_UNAUTHORIZED):
        detail_str = "Could not validate credentials"
        if detail:
            detail_str += f": {detail}"
        super().__init__(status_code=status_code, detail=detail_str, headers={"WWW-Authenticate": authenticate})


# Role exceptions
class RoleNotAssignable(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
        
class InvalidRole(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid role.")


# Image exceptions      
class InvalidImage(HTTPException):
    def __init__(self, detail: str = ""):
        detail_str = f"Invalid image file. {detail}"
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail_str)

class ImageNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
        


# Event exceptions    
class EventCreationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not create the event.")
        
class EventNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="No event found with this ID.")

class EventUserNotAuthorized(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="This user is not authorized to perform this action on this event.")
from sqlalchemy import Column, Integer, String

from app.db.base import GlobalBase

class UserSchema(GlobalBase):
    """
    Define the User schema
    A user is a person who has an account on the platform.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    profile_picture_key = Column(String, nullable=True, default=None)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    def __eq__(self, other):
        return self.email == other.email
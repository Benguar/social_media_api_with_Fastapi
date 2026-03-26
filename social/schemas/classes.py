from pydantic import BaseModel,ConfigDict,EmailStr,SecretStr,Field,conint
from datetime import datetime
class User_class(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr = Field(min_length= 8)

class Login(BaseModel):
    username: str
    password: SecretStr

class User_update(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class Posts_class(BaseModel):
    posts: str
    user_id: int | None = None

class Posts_Update(BaseModel):
    posts: str 
class Username(BaseModel):
    username: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    jti: str

class RefreshInput(BaseModel):
    user_id: int
    refresh_jti: str
    is_revoked: bool = False
    is_used: bool = False
    created_at: datetime
    expire_at: datetime
class TokenData(BaseModel):
    id: int|None = None
    jti: str| None = None

class Like(BaseModel):
    post_id: int
    dir: int
class PostResponse(BaseModel):
    posts: str
    user: Username

    model_config = ConfigDict(from_attributes=True)


class posts(BaseModel):
    posts: str

    model_config = ConfigDict(from_attributes= True)

class UserResponse(BaseModel):
    username: str
    email: str
    posts: list[posts]
    model_config = ConfigDict(from_attributes=True)
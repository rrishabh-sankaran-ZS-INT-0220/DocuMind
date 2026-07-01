from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class User(UserBase):
    id: str
    provider: str | None = None


class UserInDB(UserBase):
    id: str
    hashed_password: str | None = None
    provider: str | None = None


class OAuthLoginRequest(BaseModel):
    provider: str


class OAuthCallbackQuery(BaseModel):
    code: str
    state: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User
from fastapi import APIRouter
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.auth_service import auth_service

router = APIRouter()

@router.post("/register", status_code=201)
def register(user: UserCreate):
    """
    Register a new user via Supabase Auth and create a profile.
    """
    return auth_service.register_user(user)

@router.post("/login", response_model=Token)
def login(user: UserLogin):
    """
    Login a user via Supabase Auth and return access/refresh tokens.
    """
    return auth_service.login_user(user)

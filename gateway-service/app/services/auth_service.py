from fastapi import HTTPException, status
from app.core.supabase_client import supabase_client
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse

class AuthService:
    
    @staticmethod
    def register_user(user_data: UserCreate) -> dict:
        try:
            # 1. Sign up the user in Supabase Auth
            auth_response = supabase_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
            })
            
            user = auth_response.user
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed. User may already exist."
                )

            # 2. Automatically create the profile record linking to the auth.user
            # Supabase triggers could handle this, but doing it here explicitly ensures username capture
            profile_response = supabase_client.table('profiles').insert({
                "id": str(user.id),
                "username": user_data.username,
                "role": "analyst"
            }).execute()

            return {
                "message": "User registered successfully",
                "user_id": str(user.id)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @staticmethod
    def login_user(user_data: UserLogin) -> Token:
        try:
            # Authenticate with Supabase
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            session = auth_response.session
            if not session:
               raise HTTPException(
                   status_code=status.HTTP_401_UNAUTHORIZED,
                   detail="Invalid credentials"
               )

            return Token(
                access_token=session.access_token,
                refresh_token=session.refresh_token
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {str(e)}"
            )

auth_service = AuthService()

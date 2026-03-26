from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import supabase_client

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate the Supabase JWT token.
    Returns the user's UUID if valid.
    """
    token = credentials.credentials
    try:
        # get_user automatically validates the JWT with Supabase Edge
        user_response = supabase_client.auth.get_user(token)
        if not user_response or not user_response.user:
             raise Exception("Invalid or expired token")
        return str(user_response.user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

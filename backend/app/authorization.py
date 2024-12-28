# authorization.py

from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import decode_jwt_token

# Protect general JWTBearer token verification
class JWTBearer(HTTPBearer):
    """ To Authenticate reports at device level... """
    async def __call__(self, request: Request):  
        authorization: str = request.headers.get("Authorization")
        
        # Also allowing if no token present, handling it routes'controller
        if authorization is None:
            return None 
        
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        # print("creden",credentials)
        if not credentials:
            return None
                
        token = credentials.credentials
        payload = decode_jwt_token(token)
        if not payload:
            raise HTTPException(status_code=403, detail="Invalid or expired token")
        
        request.state.data = payload  # for Request arg
        return payload
             
             
# ---------------------AUTH0-------------------------
# Protect by Auth0 token verification

from fastapi import Depends
from fastapi_auth0 import Auth0, Auth0User

# Auth0 Configuration
auth0 = Auth0(
    domain="...auth0.com",
    api_audience="...",
)


def auth0_user_dependency(user: Optional[Auth0User] = Depends(auth0.get_user)):
    """
    A dependency that verifies the token against Auth0 and extracts the Auth0User.
    If the token is invalid or expired, it raises an HTTP 401 error.
    """
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        return user
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
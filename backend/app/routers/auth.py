"""Authentication routes for Google OAuth2."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.core import get_db, settings, create_access_token
from app.repositories import MySQLUserRepository
from starlette.requests import Request

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configure OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow.

    Returns:
        Redirect to Google OAuth consent page
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth2 callback.

    Args:
        request: Starlette request object
        db: Database session

    Returns:
        JWT token for authenticated user
    """
    try:
        # Get the authorization token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get("userinfo")
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        # Extract user data
        google_id = user_info["sub"]
        email = user_info["email"]
        display_name = user_info.get("name")
        avatar_url = user_info.get("picture")

        # Get or create user in database
        user_repo = MySQLUserRepository(db)
        user = user_repo.get_user_by_google_id(google_id)

        if not user:
            # Create new user
            user = user_repo.create_user(
                google_id=google_id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url
            )
        else:
            # Update existing user info
            user = user_repo.update_user(
                user_id=user.id,
                display_name=display_name,
                avatar_url=avatar_url
            )

        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        # In production, you might want to redirect to frontend with token
        # For now, we'll return it as JSON for testing
        frontend_url = settings.CORS_ORIGINS.split(",")[0]
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (stateless, just for API completeness).

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}

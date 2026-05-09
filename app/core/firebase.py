import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.config import get_settings

settings = get_settings()

# Initialize Firebase Admin SDK once at startup
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token sent from the React frontend.
    Returns the decoded token dict which includes:
      - uid         : Firebase user ID (unique)
      - email       : user email
      - name        : display name (Google login)
      - picture     : avatar URL (Google login)
      - sign_in_provider: 'google.com' or 'password'
    Raises ValueError if token is invalid or expired.
    """
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")

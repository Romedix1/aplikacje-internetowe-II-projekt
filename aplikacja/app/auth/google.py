import os
import requests

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SCOPES = "openid email profile"


def get_google_auth_url(state: str) -> str:
    params = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "redirect_uri": os.environ["REDIRECT_URI"],
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "access_type": "offline",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_google_code(code: str) -> dict:
    res = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "redirect_uri": os.environ["REDIRECT_URI"],
            "grant_type": "authorization_code",
        },
    )
    res.raise_for_status()
    return res.json()


def get_google_user_info(token: dict) -> dict:
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    res = requests.get(GOOGLE_USER_URL, headers=headers)
    res.raise_for_status()
    data = res.json()
    email = data.get("email", "")
    name_parts = data.get("name", "").split(" ", 1)
    return {
        "email": email,
        "first_name": name_parts[0] if name_parts else "",
        "last_name": name_parts[1] if len(name_parts) > 1 else "",
        "external_id": data.get("id"),
        "index_number": _extract_index(email),
        "provider": "google",
    }


def _extract_index(email: str) -> str | None:
    local = email.split("@")[0]
    return local if local.isdigit() and len(local) == 5 else None


def determine_google_role(email: str) -> str | None:
    from app.auth.microsoft import determine_role

    return determine_role(email)

import os
import msal
import requests


def _build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=os.environ["MICROSOFT_CLIENT_ID"],
        client_credential=os.environ["MICROSOFT_CLIENT_SECRET"],
        authority=f"https://login.microsoftonline.com/{os.environ['MICROSOFT_TENANT_ID']}",
    )


def get_auth_url(state: str) -> str:
    app = _build_msal_app()
    return app.get_authorization_request_url(
        scopes=["User.Read"], state=state, redirect_uri=os.environ["REDIRECT_URI"]
    )


def exchange_code_for_token(code: str) -> dict:
    app = _build_msal_app()
    result = app.acquire_token_by_authorization_code(
        code=code, scopes=["User.Read"], redirect_uri=os.environ["REDIRECT_URI"]
    )
    if "error" in result:
        raise ValueError(f"Błąd tokenu: {result.get('error_description')}")
    return result


def extract_index_number(email: str) -> str | None:
    local = email.split("@")[0]
    if local.isdigit():
        return local
    return None


def get_user_info(token: dict) -> dict:
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    response.raise_for_status()
    data = response.json()
    email = data.get("mail") or data.get("userPrincipalName")
    return {
        "email": email,
        "first_name": data.get("givenName", ""),
        "last_name": data.get("surname", ""),
        "external_id": data.get("id"),
        "index_number": extract_index_number(email),
        "tenant": token.get("id_token_claims", {}).get("tid"),
    }


def determine_role(email: str) -> str | None:
    student_domains = {"student.ans-elblag.pl"}

    domain = email.split("@")[-1].lower()

    if domain in student_domains:
        return "student"
    return "pending"

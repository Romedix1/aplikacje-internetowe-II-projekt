import os
import secrets
from flask import (
    Blueprint,
    redirect,
    request,
    url_for,
    session,
    render_template,
    current_app,
    jsonify,
)
from flask_login import login_user, logout_user, login_required

from app.models.user import User, db
from app.auth.microsoft import (
    get_auth_url,
    exchange_code_for_token,
    get_user_info,
    determine_role,
)
from app.auth.google import (
    get_google_auth_url,
    exchange_google_code,
    get_google_user_info,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    session["oauth_provider"] = "microsoft"
    return redirect(get_auth_url(state))


@auth_bp.route("/login/google")
def login_google():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    session["oauth_provider"] = "google"
    return redirect(get_google_auth_url(state))


@auth_bp.route("/callback")
def callback():
    expected_state = session.pop("oauth_state", None)
    received_state = request.args.get("state")
    if not expected_state or expected_state != received_state:
        print(f"[WARN] state mismatch: expected={expected_state}, got={received_state}")

    error = request.args.get("error")
    if error:
        return (
            render_template(
                "auth/error.html", message=request.args.get("error_description")
            ),
            401,
        )

    code = request.args.get("code")
    if not code:
        return (
            render_template("auth/error.html", message="Brak kodu autoryzacyjnego."),
            400,
        )

    provider = session.pop("oauth_provider", "microsoft")

    try:
        if provider == "google":
            token = exchange_google_code(code)
            user_info = get_google_user_info(token)
        else:
            token = exchange_code_for_token(code)
            user_info = get_user_info(token)
            user_info["provider"] = "microsoft"
    except Exception as e:
        print(f"[ERROR] {e}")
        return render_template("auth/error.html", message=str(e)), 500

    user = _get_or_create_user(user_info)

    if user is None:
        return (
            render_template(
                "auth/error.html", message="Twoja domena nie ma dostępu do systemu."
            ),
            403,
        )
    if not user.is_active:
        return (
            render_template(
                "auth/error.html",
                message="Konto oczekuje na zatwierdzenie przez administratora.",
            ),
            403,
        )

    login_user(user)
    return redirect(url_for("dashboard"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))


def _get_or_create_user(user_info: dict) -> User | None:
    user = User.query.filter_by(email=user_info["email"]).first()
    if user:
        return user

    provider = user_info.get("provider", "microsoft")

    if provider == "google":
        from app.auth.google import determine_google_role

        role = determine_google_role(user_info["email"])
    else:
        role = determine_role(user_info["email"])
        if role is None:
            return None

    user = User(
        email=user_info["email"],
        first_name=user_info["first_name"],
        last_name=user_info["last_name"],
        auth_provider=provider,
        external_id=user_info["external_id"],
        index_number=user_info.get("index_number"),
        role=role,
        is_active=role != "pending",
    )
    db.session.add(user)
    db.session.commit()
    return user


@auth_bp.route("/dev-login/<role>")
def dev_login(role):
    if os.environ.get("FLASK_ENV") != "development" and not current_app.debug:
        return "Not Found", 404

    debug_email = f"{role}@development.pl"

    user = User.query.filter_by(email=debug_email, role=role).first()

    if not user:
        user = User(
            email=debug_email,
            first_name="Konto",
            last_name=f"Testowe ({role.upper()})",
            role=role,
            is_active=True,
            auth_provider="debug_bypass",
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)

    return redirect(url_for("dashboard"))

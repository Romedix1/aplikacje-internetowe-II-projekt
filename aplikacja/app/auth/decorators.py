from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)

        return decorated

    return wrapper


student_required = role_required("student")
uopz_required = role_required("uopz")
zopz_required = role_required("zopz")
sekretariat_required = role_required("sekretariat")
admin_required = role_required("administrator")
staff_required = role_required("uopz", "zopz", "sekretariat", "administrator")

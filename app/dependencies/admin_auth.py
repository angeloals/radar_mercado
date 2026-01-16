from fastapi import Request
from fastapi.responses import RedirectResponse


def require_admin(request: Request):
    if not request.session.get("admin_logged"):
        return RedirectResponse("/admin/login", status_code=302)
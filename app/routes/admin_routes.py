from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import require_admin
from app.auth.utils import verify_password
from app.services.supabase_client import supabase

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request, _: None = Depends(require_admin)
) -> HTMLResponse:
    if not request.session.get("admin_logged"):
        return RedirectResponse("/admin/login", status_code=302)

    return templates.TemplateResponse(
        "admin/admin_dashboard.html", {"request": request}
    )


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "admin/admin_login.html", {"request": request}
    )


@router.post("/admin/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    result = (
        supabase.table("admin_user")
        .select("*")
        .eq("email", email)
        .single()
        .execute()
    )

    admin = result.data

    if not admin or not verify_password(password, admin["password"]):
        return RedirectResponse("/admin/login?error=1", status_code=302)

    request.session["admin_logged"] = True
    return RedirectResponse("/admin", status_code=302)

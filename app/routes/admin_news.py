from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.supabase_client import supabase
from app.utils.slug import slugify

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request):
    if not request.session.get("admin_logged"):
        return RedirectResponse("/admin/login", status_code=302)


@router.get("/admin/news/new", response_class=HTMLResponse)
def news_new(request: Request):
    require_admin(request)
    return templates.TemplateResponse(
        "admin/admin_news_form.html", {"request": request, "news": None}
    )


@router.post("/admin/news/new")
def news_create(
    title: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(...),
    # status: str = Form(...),
):
    tags_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]

    data = {
        "title": title,
        "slug": slugify(title),
        "summary": summary,
        "content": content,
        "tags": tags_list,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    # if status == "published":
    #     data["published_at"] = datetime.now(timezone.utc).isoformat()

    supabase.table("news").insert(data).execute()
    return RedirectResponse("/admin", status_code=302)


@router.get("/admin/news/{news_id}/edit", response_class=HTMLResponse)
def news_edit(request: Request, news_id: str):
    require_admin(request)
    result = supabase.table("news").select("*").eq("id", news_id).single().execute()
    return templates.TemplateResponse(
        "admin/admin_news_form.html", {"request": request, "news": result.data}
    )


@router.post("/admin/news/{news_id}/edit")
def news_update(
    request: Request,
    news_id: str,
    title: str = Form(...),
    slug: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    status: str = Form(...),
):
    require_admin(request)

    data = {
        "title": title,
        "slug": slug.lower(),
        "summary": summary,
        "content": content,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "published_at": datetime.utcnow() if status == "published" else None,
    }

    supabase.table("news").update(data).eq("id", news_id).execute()
    return RedirectResponse("/admin", status_code=302)


@router.get("/admin/news/{news_id}/delete")
def news_delete(request: Request, news_id: str):
    require_admin(request)
    supabase.table("news").delete().eq("id", news_id).execute()
    return RedirectResponse("/admin", status_code=302)

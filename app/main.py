import os
import uvicorn
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth.dependencies import require_admin
from app.models.news import NewsListItem, NewsDetail, News, NewsCreate
from app.routes.admin_news import router as admin_news_router
from app.routes.admin_routes import router as admin_router
from app.services.supabase_client import supabase

load_dotenv()

app = FastAPI()

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    max_age=60 * 60,
    same_site="lax",
    https_only=False,
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(admin_router)
app.include_router(admin_news_router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def news_list(request: Request):
    response = (
        supabase.table("news")
        .select("id, title, summary, slug, tags, status, published_at")
        .eq("status", "published")
        .order("published_at", desc=True)
        .execute()
    )

    # Convert to typed objects and format dates
    news: List[NewsListItem] = []
    for item in response.data or []:
        news_item = NewsListItem(**item)
        news_item.format_published_date()
        news.append(news_item)

    return templates.TemplateResponse(
        "public/news_list.html",
        {"request": request, "news": news},
    )


@app.get("/news/{slug}", response_class=HTMLResponse)
def news_detail(request: Request, slug: str):
    response = (
        supabase.table("news")
        .select("*")
        .eq("slug", slug)
        .eq("status", "published")
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Notícia não encontrada")

    # Convert to typed object and format date
    news = NewsDetail(**response.data)
    news.format_published_date()

    return templates.TemplateResponse(
        "public/news_detail.html",
        {"request": request, "news": news},
    )


@app.post("/admin/news", response_model=News)
def create_news(request: Request, news_data: NewsCreate):
    require_admin(request)

    # Automatically validate via Pydantic
    response = (
        supabase.table("news")
        .insert(news_data.model_dump(exclude_unset=True))
        .execute()
    )

    return News(**response.data[0])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
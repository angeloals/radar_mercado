from fastapi import Request, HTTPException


def require_admin(request: Request):
    if not request.session.get("admin_logged"):
        raise HTTPException(status_code=401, detail="Não autorizado")
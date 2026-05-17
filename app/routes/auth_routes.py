from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import os

from app.auth import (
    validate_user,
    get_user_display_name,
    get_user_header_title,
    is_mobile_device
)

router = APIRouter()

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)


# -----------------------
# Login Page
# -----------------------
@router.get("/", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request,
        "login.html",
        {}
    )


# -----------------------
# Login Submit
# -----------------------
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    if validate_user(username, password):

        request.session["user"] = username
        request.session["display_name"] = get_user_display_name(username)
        request.session["header_title"] = get_user_header_title(username)

        user_agent = request.headers.get("user-agent", "")

        if is_mobile_device(user_agent):

            return RedirectResponse(
                "/data-entry",
                status_code=303
            )

        return RedirectResponse(
            "/upload",
            status_code=303
        )

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "error": "Invalid credentials"
        }
    )


# -----------------------
# Logout
# -----------------------
@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        "/",
        status_code=303
    )

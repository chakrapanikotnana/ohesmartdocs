import pandas as pd
from fastapi import UploadFile
from fastapi.responses import FileResponse
from app.validator import validate_excel
import os
from app.pdf_service import generate_pdfs
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import (
    validate_user,
    is_logged_in,
    get_user_display_name,
    get_user_header_title,
)
from app.header_fields import (
    extract_header_values,
    get_default_header_values,
    get_header_form_fields,
)

app = FastAPI()

# Session middleware (required for login)
app.add_middleware(SessionMiddleware, secret_key="demo-secret-key")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Static files for CSS and images
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


def upload_template_context(request: Request, errors=None, header_values=None) -> dict:
    user = request.session.get("user")
    header_values = header_values or get_default_header_values(
        user,
        request.session.get("header_title"),
    )
    return {
        "errors": errors,
        "user": user,
        "display_name": request.session.get("display_name"),
        "header_fields": get_header_form_fields(header_values),
    }


# -----------------------
# Login Page
# -----------------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

# -----------------------
# Login Submit
# -----------------------
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    
    if validate_user(username, password):
        request.session["user"] = username
        request.session["display_name"] = get_user_display_name(username)
        request.session["header_title"] = get_user_header_title(username)
        return RedirectResponse("/upload", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Invalid credentials"}
    )


# -----------------------
# Upload Page
# -----------------------
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    
    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request,
        "upload.html",
        upload_template_context(request),
    )


# -----------------------
# Logout 
# -----------------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

# -----------------------
# Post Upload - Validate Excel
# -----------------------
@app.post("/upload")
async def upload_excel(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    form = await request.form()
    header_values = extract_header_values(form)
    file: UploadFile = form.get("file")

    try:
        if file is None or not getattr(file, "filename", ""):
            return templates.TemplateResponse(
                request,
                "upload.html",
                upload_template_context(
                    request,
                    errors=["Please upload an Excel file."],
                    header_values=header_values,
                ),
            )

        file.file.seek(0)
        df = pd.read_excel(file.file)

        errors = validate_excel(df)

        if errors:
            return templates.TemplateResponse(
                request,
                "upload.html",
                upload_template_context(request, errors=errors, header_values=header_values),
            )

        zip_path = generate_pdfs(
            df,
            header_values=header_values,
        )

        return FileResponse(
            path=zip_path,
            filename="output.zip",
            media_type="application/zip"
        )

    except Exception as e:
        import traceback
        return templates.TemplateResponse(
            request,
            "upload.html",
            upload_template_context(
                request,
                errors=[traceback.format_exc()],
                header_values=header_values,
            ),
        )

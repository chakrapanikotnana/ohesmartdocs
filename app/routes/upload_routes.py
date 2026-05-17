import pandas as pd
from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

import os

from app.auth import (
    is_logged_in
)

from app.validator import validate_excel
from app.pdf_service import generate_pdfs

from app.header_fields import (
    extract_header_values,
    get_default_header_values,
    get_header_form_fields,
)

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def upload_template_context(request: Request, errors=None, header_values=None):

    user = request.session.get("user")

    header_values = header_values or get_default_header_values(
        user,
        request.session.get("header_title"),
    )

    return {
        "request": request,
        "errors": errors,
        "user": user,
        "display_name": request.session.get("display_name"),
        "header_fields": get_header_form_fields(header_values),
    }


# -----------------------
# Upload Page
# -----------------------
@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request,
        "upload.html",
        upload_template_context(request),
    )


# -----------------------
# Upload Excel
# -----------------------
@router.post("/upload")
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
                upload_template_context(
                    request,
                    errors=errors,
                    header_values=header_values
                ),
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

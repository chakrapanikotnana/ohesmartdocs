import pandas as pd
import io

from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse
)

from fastapi.templating import Jinja2Templates

import os

from app.auth import is_logged_in

from app.data_fields import DATA_FIELDS

from app.storage_service import (
    save_record,
    get_unexported_records,
    mark_records_downloaded,
    get_downloaded_records,
    get_records_by_created_at
)

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# -----------------------
# Data Entry Page
# -----------------------
@router.get("/data-entry", response_class=HTMLResponse)
def data_entry_page(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request,
        "data_entry.html",
        {
            "success": False,
            "fields": DATA_FIELDS
        }
    )


# -----------------------
# Save Data
# -----------------------
@router.post("/save-data")
async def save_data(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    form = await request.form()

    record = {}

    for field in DATA_FIELDS:
        record[field] = form.get(field)

    record["username"] = request.session.get("user")

    record["download_flag"] = False

    save_record(record)

    return templates.TemplateResponse(
        request,
        "data_entry.html",
        {
            "success": True,
            "fields": DATA_FIELDS
        }
    )


# -----------------------
# Export Excel
# -----------------------
@router.get("/export-excel")
def export_excel(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    records = get_unexported_records()

    if not records:

        username = request.session.get("user")

        downloaded_records = get_downloaded_records(username)

        return templates.TemplateResponse(
            request,
            "data_entry.html",
            {
                "success": False,
                "message": "No new records available for export.",
                "show_downloaded_button": True,
                "downloaded_count": len(downloaded_records),
                "fields": DATA_FIELDS
            }
        )

    downloaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mark_records_downloaded(records, downloaded_at)

    columns = [
        "username",
        "created_at",
        "downloaded_at"
    ] + DATA_FIELDS

    df = pd.DataFrame(records)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    df = df[columns]

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")

    output.seek(0)

    username = request.session.get("user")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{username}_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# -----------------------
# Downloaded Records
# -----------------------
@router.get("/downloaded-records", response_class=HTMLResponse)
def downloaded_records_page(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    username = request.session.get("user")

    records = get_downloaded_records(username)

    return templates.TemplateResponse(
        request,
        "downloaded_records.html",
        {
            "records": records
        }
    )


# -----------------------
# Export Selected Records
# -----------------------
@router.post("/export-selected-records")
async def export_selected_records(request: Request):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    form = await request.form()

    selected_records = form.getlist("selected_records")

    records = get_records_by_created_at(selected_records)

    if not records:
        return RedirectResponse("/downloaded-records", status_code=303)

    downloaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mark_records_downloaded(records, downloaded_at)

    columns = [
        "username",
        "created_at",
        "downloaded_at"
    ] + DATA_FIELDS

    df = pd.DataFrame(records)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    df = df[columns]

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")

    output.seek(0)

    username = request.session.get("user")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{username}_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

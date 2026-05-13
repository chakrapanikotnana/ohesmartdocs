from app.demo_data import get_demo_dataframe
from app.auth import (
    get_user_header_title,
    get_user_company_line_1,
    get_user_approved_signatory_1,
    get_user_approved_signatory_2,
    get_user_approved_signatory_3,
    get_user_as_erected_footer,
)


HEADER_FIELDS = [
    {
        "name": "header_title",
        "label": "Header Title",
        "default": "GROUP No: DOUBLING CUM ELECTRIFICATION BETWEEN GUNTUR - TENALI SECTION K.M - 0.00 TO K.M - 25.00",
    },
    {"name": "company_line_1", "label": "Company", "default": "VOLTRIO SOLUTIONS",},
    {"name": "approved_signatory_1", "label": "Approved Signatory 1", "default": "RE(Ele) / PMC / GNT"},
    {"name": "approved_signatory_2", "label": "Approved Signatory 2", "default": "AM / E / RVNL / BZA"},
    {"name": "approved_signatory_3", "label": "Approved Signatory 3", "default": "JGM / E / RVNL / BZA"},
    {"name": "as_erected_footer", "label": "As Erected", "default": "For ED/ Ele /RVNL / SC"},
    
]

HEADER_RIGHT_FIELD_COLUMNS = {
    "section": "SECTION",
    "layout_no": "LAYOUT No",
    "chainage": "CHAINAGE",
    "wind_pressure": "WIND PRESSURE",
}


def _field_defaults() -> dict:
    return {field["name"]: field["default"] for field in HEADER_FIELDS}


# Maps each header field name to its corresponding auth getter function.
# This drives get_default_header_values so adding a new user field only
# requires adding an entry here (plus the getter in auth.py).
_USER_FIELD_GETTERS = {
    "header_title": get_user_header_title,
    "company_line_1": get_user_company_line_1,
    "approved_signatory_1": get_user_approved_signatory_1,
    "approved_signatory_2": get_user_approved_signatory_2,
    "approved_signatory_3": get_user_approved_signatory_3,
    "as_erected_footer": get_user_as_erected_footer,
}


def get_default_header_values(username: str, header_title: str = None) -> dict:
    values = _field_defaults()

    # Populate every field from the logged-in user's auth data so each
    # demo user sees their own defaults, not the hardcoded fallbacks.
    for field_name, getter in _USER_FIELD_GETTERS.items():
        user_value = getter(username)
        if user_value:
            values[field_name] = user_value

    # An explicit header_title argument (e.g. from a previous form submission)
    # takes precedence over the auth default.
    if header_title:
        values["header_title"] = header_title

    try:
        demo_row = get_demo_dataframe(username).iloc[0]
    except Exception:
        demo_row = None

    if demo_row is not None:
        for field_name, column_name in HEADER_RIGHT_FIELD_COLUMNS.items():
            value = demo_row.get(column_name, "")
            if value:
                values[field_name] = str(value)

    return values


def get_header_form_fields(values: dict) -> list:
    return [
        {
            **field,
            "value": values.get(field["name"], field["default"]),
        }
        for field in HEADER_FIELDS
    ]


def extract_header_values(form) -> dict:
    values = _field_defaults()
    for field in HEADER_FIELDS:
        submitted_value = form.get(field["name"])
        values[field["name"]] = str(submitted_value).strip() if submitted_value is not None else field["default"]
    return values
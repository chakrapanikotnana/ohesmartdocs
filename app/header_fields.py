from app.demo_data import get_demo_dataframe


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


def get_default_header_values(username: str, header_title: str = None) -> dict:
    values = _field_defaults()
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

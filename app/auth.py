from fastapi import Request

DEMO_USERS = {
    "demo1": {
        "password": "demo1",
        "display_name": "Guntur Section Demo",
        "header_title": "GROUP No: DOUBLING CUM ELECTRIFICATION BETWEEN GUNTUR - TENALI SECTION K.M - 0.00 TO K.M - 25.00",
        "company_line_1": "VOLTRIO SOLUTIONS",
        "approved_signatory_1": "RE(Ele) / PMC / GNT",
        "approved_signatory_2": "AM / E / RVNL / BZA",
        "approved_signatory_3": "JGM / E / RVNL / BZA",
        "as_erected_footer": "For ED/ Ele /RVNL / SC",
    },
    "demo2": {
        "password": "demo2",
        "display_name": "Tenali Yard Demo",
        "header_title": "GROUP No: DEMO 2 - TENALI YARD OHE LAYOUT AND ELECTRIFICATION WORKS",
        "company_line_1": "Novuslogix Engineering",
        "approved_signatory_1": "RE(Ele) / PMC / ABC",
        "approved_signatory_2": "AM / E / RVNL / DEF",
        "approved_signatory_3": "JGM / E / RVNL / GHI",
        "as_erected_footer": "For ED/ Ele /RVNL / JKL",
    },
    "demo3": {
        "password": "demo3",
        "display_name": "Bridge Approach Demo",
        "header_title": "GROUP No: DEMO 3 - BRIDGE APPROACH OHE LAYOUT AND MAST SCHEDULE",
        "company_line_1": "L&T Construction",
        "approved_signatory_1": "RE(Ele) / PMC / XYZ",
        "approved_signatory_2": "AM / E / RVNL / MNO",
        "approved_signatory_3": "JGM / E / RVNL / PQR",
        "as_erected_footer": "For ED/ Ele /RVNL / EF",
    },
}

def validate_user(username: str, password: str) -> bool:
    user = DEMO_USERS.get(username)
    return user is not None and user["password"] == password


def get_user_display_name(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("display_name", username)


def get_user_header_title(username: str) -> str:
    return DEMO_USERS.get(username, {}).get(
        "header_title",
        "GROUP No: DOUBLING CUM ELECTRIFICATION BETWEEN GUNTUR - TENALI SECTION K.M - 0.00 TO K.M - 25.00",
    )


def get_user_company_line_1(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("company_line_1", "")


def get_user_approved_signatory_1(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("approved_signatory_1", "")


def get_user_approved_signatory_2(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("approved_signatory_2", "")


def get_user_approved_signatory_3(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("approved_signatory_3", "")


def get_user_as_erected_footer(username: str) -> str:
    return DEMO_USERS.get(username, {}).get("as_erected_footer", "")


def is_logged_in(request: Request) -> bool:
    return request.session.get("user") is not None

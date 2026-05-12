from fastapi import Request

DEMO_USERS = {
    "demo1": {
        "password": "demo1",
        "display_name": "Guntur Section Demo",
        "header_title": "GROUP No: DOUBLING CUM ELECTRIFICATION BETWEEN GUNTUR - TENALI SECTION K.M - 0.00 TO K.M - 25.00",
    },
    "demo2": {
        "password": "demo2",
        "display_name": "Tenali Yard Demo",
        "header_title": "GROUP No: DEMO 2 - TENALI YARD OHE LAYOUT AND ELECTRIFICATION WORKS",
    },
    "demo3": {
        "password": "demo3",
        "display_name": "Bridge Approach Demo",
        "header_title": "GROUP No: DEMO 3 - BRIDGE APPROACH OHE LAYOUT AND MAST SCHEDULE",
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


def is_logged_in(request: Request) -> bool:
    return request.session.get("user") is not None

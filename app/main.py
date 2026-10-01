import json
import uuid

from datetime import datetime, timezone

from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from fastapi.staticfiles import (
    StaticFiles
)


from .config import (
    UPLOAD_DIR,
    MAX_UPLOAD_MB,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from .db import (
    init_db,
    fetch_one,
    fetch_all,
    execute
)

from .auth import (
    hash_password,
    login_user,
    get_current_user,
    logout_user
)

from .schemas import (
    RegisterInput,
    HomeBudgetInput,
    PartyBudgetInput,
    JewelryBudgetInput
)

from .recommender import (
    home,
    party,
    jewelry
)


# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title="PocketSmart AI",
    description=(
        "Smart Budget & Recommendation Assistant"
    ),
    version="1.0.0"
)


# =========================================================
# Templates
# =========================================================

templates = Jinja2Templates(
    directory=str(
        Path(__file__).parent / "templates"
    )
)


# =========================================================
# Static files
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(
            Path(__file__).parent / "static"
        )
    ),
    name="static"
)


# =========================================================
# Startup
# =========================================================

@app.on_event("startup")
def startup():

    init_db()

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# =========================================================
# Helpers
# =========================================================

def render_page(
    request: Request,
    template_name: str,
    **context
):

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            **context
        }
    )


def require_user(
    request: Request
):

    return get_current_user(
        request
    )


def save_recommendation(
    user,
    recommendation_type,
    input_data,
    result
):

    recommendation_id = str(
        uuid.uuid4()
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    suggestions = result.get(
        "additional_suggestions",
        []
    )

    if suggestions:

        summary = str(
            suggestions[0]
        )

    else:

        summary = (
            "Budget recommendation generated."
        )

    execute(
        """
        INSERT INTO recommendations (
            id,
            username,
            recommendation_type,
            timestamp,
            input_json,
            result_json,
            result_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            recommendation_id,
            user["username"],
            recommendation_type,
            timestamp,
            json.dumps(
                input_data,
                ensure_ascii=False
            ),
            json.dumps(
                result,
                ensure_ascii=False
            ),
            summary
        )
    )

    return recommendation_id


# =========================================================
# Public pages
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def index(request: Request):

    return render_page(
        request,
        "index.html"
    )


@app.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    return render_page(
        request,
        "login.html"
    )


@app.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(request: Request):

    return render_page(
        request,
        "register.html"
    )


# =========================================================
# Registration
# =========================================================

@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...)
):
    existing = fetch_one(
        """
        SELECT id
        FROM users
        WHERE username = ?
        OR email = ?
        """,
        (
            username,
            email
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists."
        )

    execute(
        """
        INSERT INTO users (
            username,
            email,
            full_name,
            password_hash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            email,
            full_name,
            hash_password(password),
            datetime.now(timezone.utc).isoformat()
        )
    )

    return RedirectResponse(
        url="/login",
        status_code=303
    )


# =========================================================
# Login
# =========================================================

@app.post("/token")
def token(
    username: str = Form(...),
    password: str = Form(...)
):

    access_token = login_user(
        username,
        password
    )

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail=(
                "Incorrect username or password."
            )
        )

    response = JSONResponse(
        {
            "access_token":
                access_token,

            "token_type":
                "bearer"
        }
    )

    response.set_cookie(

        key="access_token",

        value=access_token,

        httponly=True,

        max_age=(
            ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        ),

        samesite="lax",

        secure=False
    )

    return response


# =========================================================
# Logout
# =========================================================

@app.post("/logout")
def logout(
    request: Request
):

    token = request.cookies.get(
        "access_token"
    )

    logout_user(
        token
    )

    response = RedirectResponse(
        "/login",
        status_code=303
    )

    response.delete_cookie(
        "access_token"
    )

    return response


# =========================================================
# Protected pages
# =========================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(
    request: Request
):

    user = require_user(
        request
    )

    return render_page(
        request,
        "dashboard.html",
        user=user
    )


@app.get(
    "/home-planner",
    response_class=HTMLResponse
)
def home_planner(
    request: Request
):

    user = require_user(
        request
    )

    return render_page(
        request,
        "home_planner.html",
        user=user
    )


@app.get(
    "/party-planner",
    response_class=HTMLResponse
)
def party_planner(
    request: Request
):

    user = require_user(
        request
    )

    return render_page(
        request,
        "party_planner.html",
        user=user
    )


@app.get(
    "/jewelry-planner",
    response_class=HTMLResponse
)
def jewelry_planner(
    request: Request
):

    user = require_user(
        request
    )

    return render_page(
        request,
        "jewelry_planner.html",
        user=user
    )


@app.get(
    "/history",
    response_class=HTMLResponse
)
def history_page(
    request: Request
):

    user = require_user(
        request
    )

    return render_page(
        request,
        "history.html",
        user=user
    )


# =========================================================
# HOME API
# =========================================================

@app.post("/api/home-budget")
def home_budget(
    data: HomeBudgetInput,
    request: Request
):

    user = require_user(
        request
    )

    result = home(
        data
    )

    recommendation_id = (
        save_recommendation(
            user,
            "home",
            data.model_dump(),
            result
        )
    )

    result["id"] = recommendation_id

    return result


# =========================================================
# PARTY API
# =========================================================

@app.post("/api/party-budget")
def party_budget(
    data: PartyBudgetInput,
    request: Request
):

    user = require_user(
        request
    )

    result = party(
        data
    )

    recommendation_id = (
        save_recommendation(
            user,
            "party",
            data.model_dump(),
            result
        )
    )

    result["id"] = recommendation_id

    return result


# =========================================================
# JEWELRY API
# =========================================================

@app.post("/api/jewelry-budget")
async def jewelry_budget(

    request: Request,

    total_budget: float = Form(...),

    occasion: str = Form(...),

    preferences: str = Form(""),

    image: UploadFile | None = File(
        default=None
    )
):

    user = require_user(
        request
    )

    data = JewelryBudgetInput(

        total_budget=total_budget,

        occasion=occasion,

        preferences=preferences
    )

    image_path = None

    # -----------------------------------------------------
    # Optional image upload
    # -----------------------------------------------------

    if image and image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG or WEBP "
                    "images are supported."
                )
            )

        image_bytes = await image.read()

        maximum_bytes = (
            MAX_UPLOAD_MB
            * 1024
            * 1024
        )

        if len(image_bytes) > maximum_bytes:

            raise HTTPException(
                status_code=413,
                detail=(
                    f"Image must be smaller "
                    f"than {MAX_UPLOAD_MB} MB."
                )
            )

        extension = (
            Path(
                image.filename
            ).suffix.lower()
            or ".jpg"
        )

        filename = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )

        image_path = (
            UPLOAD_DIR
            / filename
        )

        image_path.write_bytes(
            image_bytes
        )

        execute(
            """
            INSERT INTO uploads (
                username,
                filename,
                path,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user["username"],
                image.filename,
                str(image_path),
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        )

    result = jewelry(
        data,
        str(image_path)
        if image_path
        else None
    )

    recommendation_id = (
        save_recommendation(
            user,
            "jewelry",
            data.model_dump(),
            result
        )
    )

    result["id"] = recommendation_id

    return result


# =========================================================
# Recommendation history
# =========================================================

@app.get("/api/history")
def api_history(
    request: Request
):

    user = require_user(
        request
    )

    rows = fetch_all(
        """
        SELECT
            id,
            timestamp,
            recommendation_type,
            input_json,
            result_summary
        FROM recommendations
        WHERE username = ?
        ORDER BY timestamp DESC
        """,
        (
            user["username"],
        )
    )

    history = []

    for row in rows:

        history.append({

            "id":
                row["id"],

            "timestamp":
                row["timestamp"],

            "type":
                row["recommendation_type"],

            "input":
                json.loads(
                    row["input_json"]
                ),

            "summary":
                row["result_summary"]
        })

    return {
        "history":
            history
    }


# =========================================================
# History detail
# =========================================================

@app.get(
    "/api/history/{recommendation_id}"
)
def history_detail(
    recommendation_id: str,
    request: Request
):

    user = require_user(
        request
    )

    row = fetch_one(
        """
        SELECT *
        FROM recommendations
        WHERE id = ?
        AND username = ?
        """,
        (
            recommendation_id,
            user["username"]
        )
    )

    if not row:

        raise HTTPException(
            status_code=404,
            detail=(
                "Recommendation not found."
            )
        )

    return {

        "id":
            row["id"],

        "timestamp":
            row["timestamp"],

        "type":
            row["recommendation_type"],

        "input":
            json.loads(
                row["input_json"]
            ),

        "full_result":
            json.loads(
                row["result_json"]
            )
    }


# =========================================================
# Session information
# =========================================================

@app.get("/api/session-info")
def session_info(
    request: Request
):

    user = require_user(
        request
    )

    return {

        "username":
            user["username"],

        "email":
            user["email"],

        "full_name":
            user["full_name"]
    }


# =========================================================
# Health check
# =========================================================

@app.get("/health")
def health():

    return {

        "status":
            "ok",

        "service":
            "pocketsmart"
    }
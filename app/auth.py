from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request

from jose import JWTError, jwt

from passlib.context import CryptContext

from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from .db import (
    execute,
    fetch_one
)


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def now_iso():
    """
    Return current UTC time as ISO string.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def hash_password(password: str) -> str:
    """
    Hash user password.
    """

    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str
) -> bool:

    return pwd_context.verify(
        password,
        password_hash
    )


# ---------------------------------------------------------
# JWT
# ---------------------------------------------------------

def create_token(username: str) -> str:
    """
    Create JWT authentication token.
    """

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_cookie_token(request: Request):
    """
    Get JWT from HttpOnly cookie.
    """

    return request.cookies.get(
        "access_token"
    )


# ---------------------------------------------------------
# Current user
# ---------------------------------------------------------

def get_current_user(request: Request):
    """
    Validate session and return logged-in user.
    """

    token = get_cookie_token(request)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise ValueError()

    except (JWTError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    session = fetch_one(
        """
        SELECT *
        FROM sessions
        WHERE token = ?
        AND username = ?
        """,
        (
            token,
            username
        )
    )

    user = fetch_one(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    if not session or not user:

        raise HTTPException(
            status_code=401,
            detail="Session not found"
        )

    execute(
        """
        UPDATE sessions
        SET last_activity = ?
        WHERE id = ?
        """,
        (
            now_iso(),
            session["id"]
        )
    )

    return user


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

def login_user(
    username: str,
    password: str
):

    user = fetch_one(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    if not user:
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    token = create_token(username)

    # Keep one active session per user
    execute(
        """
        DELETE FROM sessions
        WHERE username = ?
        """,
        (username,)
    )

    current_time = now_iso()

    execute(
        """
        INSERT INTO sessions (
            username,
            token,
            login_time,
            last_activity
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            token,
            current_time,
            current_time
        )
    )

    return token


def logout_user(token):
    """
    Delete current session.
    """

    if token:

        execute(
            """
            DELETE FROM sessions
            WHERE token = ?
            """,
            (token,)
        )
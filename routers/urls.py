from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
import sqlite3
from database import get_connection, URLS_TABLE
from schemas import UrlCreate, UrlResponse
from utils import is_valid_url, generate_code
from logging_config import logger

router = APIRouter()

@router.post("/shorten", response_model=UrlResponse)
async def shorten_url(request: Request, data: UrlCreate):
    original_url = str(data.url).rstrip("/")
    if not is_valid_url(original_url):
        logger.error(f"Invalid URL: {original_url}")
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        code = generate_code()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {URLS_TABLE} (original_url, code) VALUES (?, ?)", (original_url, code))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Validation error")

    short_url = f"{request.base_url}{code}"
    return UrlResponse(short_url=short_url)

@router.get("/{code}")
async def redirect_to_url(code: str):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT original_url FROM {URLS_TABLE} WHERE code = ?", (code,)
            )
            row = cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    if row is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url=row[0])
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
import sqlite3
from database import get_connection
from schemas import UrlCreate, UrlResponse
from utils import is_valid_url, generate_code
from logging_config import logger

router = APIRouter()

@router.post("/shorten", response_model=UrlResponse)
async def shorten_url(request: Request, data: UrlCreate):
    original_url = str(data.url)
    if not is_valid_url(original_url):
        logger.error(f"Invalid URL: {original_url}")
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        code = generate_code()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO urls (original_url, code) VALUES (?, ?)", (original_url, code))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Validation error")

    return UrlResponse(url=request.url_for("redirect_to_url", code=code), code=code)

@router.get("/{code}")
async def redirect_to_url(code: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM urls WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row is None:
            logger.error(f"Code URL not found: {code}")
            raise HTTPException(status_code=404, detail="URL not found")
        original_url = row[0]
        logger.info(f"Redirecting from code {code} to URL: {original_url}")
        return RedirectResponse(url=original_url)
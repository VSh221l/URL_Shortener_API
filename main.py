from contextlib import asynccontextmanager
from fastapi import FastAPI
from logging_config import logger
from routers.urls import router as urls_router
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database")
    init_db()
    yield

app = FastAPI(
    title="URL Shortener API", 
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(urls_router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the URL Shortener API"}
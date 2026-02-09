from pydantic import BaseModel, HttpUrl

class UrlCreate(BaseModel):
    url: HttpUrl

class UrlResponse(UrlCreate):
    short_url: str
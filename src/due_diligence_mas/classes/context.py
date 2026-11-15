from pydantic import BaseModel


class Location(BaseModel):
    city: str
    timezone: str
    country: str
    region: str


class CurrentContext(BaseModel):
    location: Location | str
    date_time: str

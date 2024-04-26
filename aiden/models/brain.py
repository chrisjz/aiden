from pydantic import BaseModel


class SensoryData(BaseModel):
    vision: str = ""
    auditory: str = ""
    tactile: str = ""
    smell: str = ""
    taste: str = ""

from pydantic import BaseModel


class Sensory(BaseModel):
    vision: str = ""
    auditory: str = ""
    tactile: str = ""
    olfactory: str = ""
    gustatory: str = ""

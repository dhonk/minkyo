from pydantic import BaseModel, Field
from core.config import settings

class matches(BaseModel):
    start_offset: int = Field(alias='startOffset')
    end_offset: int = Field(alias='endOffset')

class predictionText(BaseModel):
    text: str
    matches: list[matches]

class placePrediction(BaseModel):
    place: str
    place_id: str = Field(alias='placeId')
    text: predictionText

class gmap_client():
    def __init__(self):
        self.api_key: str = settings.gmaps_api_key

    def get_place(self, input_str: str) -> dict:
        url: str = 'https://places.googleapis.com/v1/places:autocomplete'

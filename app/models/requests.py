from pydantic import BaseModel, Field



class ExtractRequest(BaseModel):
    raw_text: str  = Field(min_length=1, max_length=2000)
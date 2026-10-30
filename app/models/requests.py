import binascii

from pydantic import BaseModel, Field, ValidationError, field_validator
import base64


class ExtractRequest(BaseModel):
    raw_text: str
    
class ImageExtractRequest(BaseModel):
    image_data: str
    mime_type: str

    @field_validator("image_data")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        try:
            base64.b64decode(v, validate=True)  
            
        except binascii.Error as e:
            raise ValueError("Error, please upload an image")
    
        return v
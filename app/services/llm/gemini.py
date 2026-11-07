# app/services/llm/gemini.py

import base64
from pydantic import ValidationError
from google import genai
from google.genai import types
import json
import logging
from app.models.expense import Expense
from app.services.llm.prompts import build_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiClient:
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)


    def _build_config(self, input_type: str = "text") -> types.GenerateContentConfig:

        return types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=1500,
            system_instruction=build_prompt(input_type)
        )
    

    async def extract_expense(self, raw_input: str) -> Expense:
        # clean the input
        llm_input= raw_input.strip()

        # check if empty, raise ValueError if it is
        if not llm_input:
            raise ValueError("The input is empty. Please enter something before making request")      

        try:
            config = self._build_config("text")
            # Step 1: send raw_input to gemini, await the response
            response = await self.client.aio.models.generate_content(
                            model=settings.PRIMARY_MODEL,
                            contents=llm_input,
                            config=config
                        )

            # Step 2: convert response.text from string to python dictionary
            raw_json = json.loads(response.text)

            # Step 3: pass dictionary into Expense model for validation
            expense= Expense(**raw_json)

            # Step 4: return the validated expense
            return expense

        except json.JSONDecodeError as e:
            # log the error message and the first 200 chars of the bad response
            # then raise a ValueError explaining JSON was invalid
            logger.error(f"Decoding JSON failed: {e} | Response was: {response.text}")
            raise ValueError("JSON data is invalid")

        except ValidationError as e:
            # log the error
            # then raise a ValueError explaining pydantic validation failed
            logger.error(f"Pydantic validation failed: {e}")
            raise ValueError("Data failed to pass pydantic validation")
        

        except Exception as e:
            # log the error
            # then raise a ValueError explaining the API call failed
            logger.error(f"Exception occured: {e}")
            raise ValueError("There was error in response retreival")


    async def extract_expense_from_image(self, image_data: str, mime_type: str) -> Expense:
        decoded = base64.b64decode(image_data)

        image_part = types.Part.from_bytes(
                                data=decoded,
                                mime_type=mime_type
                            )
        text_part = "Extract the expense details from this receipt image."

   

        try:

            config = self._build_config("image")
            response = await self.client.aio.models.generate_content(
                                        model=settings.PRIMARY_MODEL,
                                        contents=[image_part, text_part],
                                        config=config
                                    )
            
           
            raw_json= json.loads(response.text)
           
            expense= Expense(**raw_json)

            return expense

        except json.JSONDecodeError as e:
            logger.error(f"Decoding JSON failed: {e} | Response: {response.text[:200]}")
            raise ValueError("JSON data is invalid")

        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValueError("Data failed to pass pydantic validation")

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            raise ValueError("There was an error in response retrieval")
                
# app/services/llm/gemini.py

import base64

from pydantic import ValidationError

import google.generativeai as genai
import json
import logging
from app.models.expense import Expense
from app.services.llm.prompts import build_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiClient:
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("GeminiClient ready")

    async def extract_expense(self, raw_input: str) -> Expense:
        # clean the input
        llm_input= raw_input.strip()

        # check if empty, raise ValueError if it is
        if not llm_input:
            raise ValueError("The input is empty. Please enter something before making request")

        # rebuild model with fresh prompt
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=500
            ),
            system_instruction=build_prompt()
        )

        try:
            # Step 1: send raw_input to gemini, await the response
            response = await model.generate_content_async(llm_input)

            # Step 2: convert response.text from string to python dictionary
            raw_json = json.loads(response.text)

            # Step 3: pass dictionary into Expense model for validation
            expense= Expense(**raw_json)

            # Step 4: return the validated expense
            return expense

        except json.JSONDecodeError as e:
            # log the error message and the first 200 chars of the bad response
            # then raise a ValueError explaining JSON was invalid
            logger.error(f"Decoding JSON failed: {e} | Response was: {response.text[:200]}")
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

        image_part = {"mime_type": mime_type, "data": decoded}
        text_part = "Extract the expense details from this receipt image."

        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=500
            ),
            system_instruction=build_prompt()
        )

        try:
            
            response= await model.generate_content_async([image_part, text_part])
           
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
                
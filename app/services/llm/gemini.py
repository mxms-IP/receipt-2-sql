# app/services/llm/gemini.py

import base64
from http.client import HTTPException
from pydantic import ValidationError
from google import genai
from google.genai import types
import json
import logging
from app.models.expense import Expense, ExpenseBatch
from app.services.llm.prompts import build_prompt, build_structural_prompt
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

    def _log_usage(self, response, ) -> None:
            usage = response.usage_metadata
            if usage is None:
                logger.warning(f"No usage metadata returned")
                return
            print(
                f"Tokens -> "
                f"prompt: {usage.prompt_token_count}, "
                f"output: {usage.candidates_token_count}, "
                f"thinking: {usage.thoughts_token_count}, "
                f"total: {usage.total_token_count}"
            )
    @staticmethod
    def parse_batch(raw_json: dict) -> tuple[list[Expense], list[dict]]:
            valid = []
            failed = []
    
            batch = ExpenseBatch.model_validate(raw_json)   # shape check only
    
            for index, item in enumerate(batch.expenses):
                try:
                    expense= Expense.model_validate(item)
                    valid.append(expense)
                except ValidationError as e:
                    failed.append({"index": index, "reason": e.errors()[0]["msg"]})
                    
    
            return valid, failed

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
                            contents= build_structural_prompt(llm_input),
                            config=config
                        )

            self._log_usage(response)
           
            raw_json = json.loads(response.text)
            print("----------------------Received-------------------------------")
            print(raw_json)
            raw_json["expenses"][0]["amount"] = -5.00
            expense= self.parse_batch(raw_json)
          
            return { "valid": expense[0], "failed": expense[1]}

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

    
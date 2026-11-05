import httpx
import json
import logging
from pydantic import ValidationError

from app.models.expense import Expense
from app.services.llm.prompts import build_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = settings.FALLBACK_MODEL


class OpenRouterClient:

    def _build_headers(self) -> dict:
        # Return a dict with two keys:

        return {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

    def _build_text_payload(self, user_input: str) -> dict:
        # Return the full request body as a dict:

        return {
            "model": MODEL,
            "messages": 
                [ 
                    {"role": "system", "content": build_prompt("text")},
                    {"role": "user", "content": user_input},
                   
                ],
            "response_format": {"type": "json_object"}
            
        }

    def _build_image_payload(self, image_data: str, mime_type: str) -> dict:
         
         return {
                    "model": MODEL,
                    "messages": 
                        [
                            {"role": "system", "content": build_prompt("image")},
                            { "role": "user", "content": 
                                [
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                                    },
                                    {
                                        "type": "text",
                                        "text": "Extract the expense details from this receipt."
                                    }
                                ]
                            }
                        ],
                    "response_format": {"type": "json_object"} 
                }

    async def extract_expense(self, raw_input: str) -> Expense:
        # 1. Strip and validate raw_input (raise ValueError if empty)
        input = raw_input.strip()

        if not input:
            raise ValueError("Input is empty")

        # 2. Build headers and payload using the helpers above
        header= self._build_headers()
        payload= self._build_text_payload(input)

        async with httpx.AsyncClient() as client: 
            response = await client.post(OPENROUTER_URL, headers=header, json=payload) 
            if response.status_code != 200:
                raise ValueError("Response failed")

        try: 
            response_data = response.json()
            raw_json = response_data["choices"][0]["message"]["content"]

            raw_dict= json.loads(raw_json)

            expense= Expense(**raw_dict)

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
            
        
        return expense

    async def extract_expense_from_image(self, image_data: str, mime_type: str) -> Expense:

        header= self._build_headers()
        payload= self._build_image_payload(image_data, mime_type)

        async with httpx.AsyncClient() as client: 
            response = await client.post(OPENROUTER_URL, headers=header, json=payload)
            if response.status_code != 200:
                raise ValueError("Response failed")

        try: 
            response_data = response.json()
            raw_json = response_data["choices"][0]["message"]["content"]

            raw_dict= json.loads(raw_json)

            expense= Expense(**raw_dict)

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
            
        
        return expense
import whisper
import asyncio

class WhisperClient:
    
    def __init__(self):
        self.model = whisper.load_model("base")  # load the base model
    
    async def transcribe(self, audio_path: str) -> str:
        result= await asyncio.get_running_loop().run_in_executor(None, self.model.transcribe, audio_path)
        
        return result["text"].strip()
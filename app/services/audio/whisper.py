import whisper
import asyncio

class WhisperClient:
    
    def __init__(self):
        self.model = whisper.load_model("base")  # load the base model
    
    async def transcribe(self, audio_path: str) -> str:
        result= await asyncio.get_event_loop().run_in_executor(None, self.model.transcribe, audio_path)
        result = self.model.transcribe(audio_path)  # transcribe the audio file
        return result["text"].strip()
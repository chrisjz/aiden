from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse
from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile
import numpy as np
import logging

app = FastAPI()

model = VitsModel.from_pretrained("facebook/mms-tts-eng")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")

logger = logging.getLogger("uvicorn")


@app.post("/synthesize/")
async def synthesize(text: str = Form(...)):
    try:
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = model(**inputs).waveform
        output_file = "output.wav"

        # Ensure the waveform data is in the correct range for int16
        wav_data = np.int16(output.numpy()[0] * 32767)
        scipy.io.wavfile.write(
            output_file, rate=model.config.sampling_rate, data=wav_data
        )

        def iterfile():
            with open(output_file, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="audio/wav")
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, File, UploadFile
import whisper
import soundfile as sf
import io

app = FastAPI()


@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Load the Whisper model
    model = whisper.load_model("tiny.en")

    # Read the audio file
    audio_data, _ = sf.read(io.BytesIO(await file.read()), dtype="float32")

    # Transcribe the audio
    result = model.transcribe(audio_data)

    return {"transcription": result["text"]}

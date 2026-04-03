from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import edge_tts
import uuid
import os
import asyncio

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder to store audio files
AUDIO_FOLDER = "audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Serve the audio files at /audio
app.mount("/audio", StaticFiles(directory=AUDIO_FOLDER), name="audio")

# Predefined Q&A in Telugu
DEFAULT_QA = {
    # Agriculture
    "మొక్కలు ఎలా నాటాలి?": [
        "మట్టిని తగిన స్థలంలో ఎంపిక చేయండి",
        "బీజాలను సమంగా నాటండి",
        "ప్రతినిత్యం నీరు ఇవ్వండి",
        "మొక్కల సంరక్షణ చేయండి"
    ],
    # Bank
    "బ్యాంక్ అకౌంట్ ఎలా తెరవాలి?": [
        "సంఖ్యాత్మక డాక్యుమెంట్లను సిద్ధం చేయండి",
        "నిజమైన బ్యాంక్ బ్రాంచ్‌కి వెళ్లండి",
        "ఫారమ్ పూర్ణం చేసి సబ్మిట్ చేయండి",
        "అకౌంట్ ప్రారంభించబడుతుంది"
    ],
    # Hospital
    "ప్రైవేటు హాస్పిటల్ లో అపాయింట్‌మెంట్ ఎలా బుక్ చేయాలి?": [
        "హాస్పిటల్ వెబ్‌సైట్ లేదా కాల్ సెంటర్‌ని తెరవండి",
        "డాక్టర్ మరియు టైం ఎంచుకోండి",
        "వివరాలు సరైనవిగా ఇచ్చండి",
        "కన్ఫర్మేషన్ పొందండి"
    ],
    # Government services
    "ప్రభుత్వ సర్వీసులు ఎలా పొందాలి?": [
        "సంబంధిత ప్రభుత్వ వెబ్‌సైట్ సందర్శించండి",
        "తగిన డాక్యుమెంట్లు సిద్ధం చేసుకోండి",
        "ఫారమ్ పూర్ణం చేసి సబ్మిట్ చేయండి",
        "సేవ పొందడానికి కన్ఫర్మేషన్ పొందండి"
    ],
    # General info
    "పాస్‌పోర్ట్ కోసం ఎలా అప్లై చేయాలి?": [
        "ఆధార్ మరియు ఫోటో సిద్ధం చేసుకోండి",
        "ఆన్‌లైన్ ఫారమ్ భర్తీ చేయండి",
        "పెర్మనెంట్ అడ్రెస్ ప్రూఫ్ ఇవ్వండి",
        "అపాయింట్‌మెంట్‌కి వెళ్ళి కన్ఫర్మ్ చేయండి"
    ]
}

async def generate_audio(text: str):
    """
    Generates a single mp3 audio for all steps combined
    """
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)

    communicate = edge_tts.Communicate(text, voice="te-IN-ShrutiNeural")
    await communicate.save(filepath)

    return f"/audio/{filename}"

@app.get("/")
def root():
    return {"message": "Telugu AI Voice Assistant Running"}

@app.get("/ask")
async def ask_question(question: str):
    """
    Returns steps and one combined audio file for the entire answer
    """
    question = question.strip().lower()

    steps = DEFAULT_QA.get(question, [
        "క్షమించండి, ఆ ప్రశ్నకు సమాధానం అందుబాటులో లేదు",
        "దయచేసి వేరే ప్రశ్న అడగండి",
        "ఇంటర్నెట్ కనెక్షన్ తనిఖీ చేయండి",
        "తాజా సమాచారం కోసం మళ్లీ ప్రయత్నించండి"
    ])

    # Combine all steps into one text for audio
    speech_text = ". ".join(steps)
    audio_url = await generate_audio(speech_text)

    return {
        "steps": steps,
        "audio": audio_url
    }

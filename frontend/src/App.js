import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [audioUrl, setAudioUrl] = useState(""); // single audio for all steps
  const recorded = useRef(false); // track if question is already asked
  const recognitionRef = useRef(null);

  const images = [
    "https://cdn-icons-png.flaticon.com/512/684/684908.png",
    "https://cdn-icons-png.flaticon.com/512/2920/2920349.png",
    "https://cdn-icons-png.flaticon.com/512/2921/2921222.png",
    "https://cdn-icons-png.flaticon.com/512/2921/2921226.png"
  ];

  const startListening = () => {
    if (recorded.current) {
      alert("ప్రశ్న ఇప్పటికే అడిగారు. కొత్త ప్రశ్న కోసం పేజీని రిఫ్రెష్ చేయండి.");
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition supported కాదు.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "te-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognitionRef.current = recognition;

    recognition.start();
    setListening(true);

    recognition.onresult = async (event) => {
      const speechText = event.results[0][0].transcript;
      setQuestion(speechText);
      setLoading(true);

      try {
        const res = await axios.get(
          `http://127.0.0.1:8000/ask?question=${encodeURIComponent(speechText)}`
        );

        setSteps(res.data.steps);
        setAudioUrl(res.data.audio); // single audio
        recorded.current = true; // mark question as asked
      } catch (error) {
        console.error("API Error:", error);
      }

      setLoading(false);
      setListening(false);
    };

    recognition.onerror = () => {
      setListening(false);
      setLoading(false);
    };
  };

  return (
    <div className="container">
      <h1 className="title">Visual Guide</h1>

      <div className="controls">
        <button
          onClick={startListening}
          disabled={listening || recorded.current}
          className={`btn start ${listening ? "recording" : ""}`}
        >
          {listening ? "🎙 Recording..." : "🎤 Start"}
        </button>
      </div>

      <div className="qa-box">
        <h3>Question</h3>
        <p>{question}</p>

        <h2>Step-by-Step Guide</h2>
        {loading && <h3 className="thinking">🤖 Thinking...</h3>}

        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={index} className="step">
              <img src={images[index % images.length]} alt="step" />
              <p><b>{index + 1}.</b> {step}</p>
            </div>
          ))}
        </div>

        {audioUrl && (
          <div className="audio-container">
            <h3>Listen to all steps:</h3>
            <audio controls src={audioUrl} className="audio-player" />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
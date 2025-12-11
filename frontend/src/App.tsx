import React, { useState, useEffect } from "react";
import { AvatarDisplay } from "./components/AvatarDisplay";
import { useVAD } from "./hooks/useVAD";
import { useWebSocket } from "./hooks/useWebSocket";
import "./App.css";

const ANAM_API_KEY = import.meta.env.VITE_ANAM_API_KEY || "";

function App() {
    const [inputText, setInputText] = useState("");
    const [isAvatarReady, setIsAvatarReady] = useState(false);

    const {
        isListening,
        isSpeaking,
        startListening,
        stopListening,
        audioChunks,
        clearChunks,
    } = useVAD();

    const {
        isConnected,
        sendAudioChunk,
        sendAudioEnd,
        sendTextQuery,
        transcription,
        response,
        error: wsError,
    } = useWebSocket();

    // Send audio chunks when VAD collects them (2-second buffers)
    useEffect(() => {
        if (audioChunks.length > 0 && !isSpeaking) {
            // User stopped speaking, send all chunks
            audioChunks.forEach((chunk) => sendAudioChunk(chunk));
            sendAudioEnd();
            clearChunks();
        }
    }, [audioChunks, isSpeaking, sendAudioChunk, sendAudioEnd, clearChunks]);

    const handleTextSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputText.trim()) {
            sendTextQuery(inputText);
            setInputText("");
        }
    };

    const handleVoiceToggle = () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1>🧠 AI Council</h1>
                <p className="subtitle">Committee of Minds</p>
            </header>

            <main className="app-main">
                {/* Avatar Display */}
                <section className="avatar-section">
                    <AvatarDisplay
                        apiKey={ANAM_API_KEY}
                        responseText={response?.final_response}
                        onReady={() => setIsAvatarReady(true)}
                    />
                </section>

                {/* Status Indicators */}
                <section className="status-section">
                    <div className="status-indicators">
                        <div
                            className={`status-indicator ${
                                isConnected ? "connected" : "disconnected"
                            }`}
                        >
                            {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
                        </div>

                        {isAvatarReady && (
                            <div className="status-indicator connected">
                                🎭 Avatar Ready
                            </div>
                        )}

                        {isListening && (
                            <div
                                className={`status-indicator ${
                                    isSpeaking ? "speaking" : "listening"
                                }`}
                            >
                                {isSpeaking
                                    ? "🎤 Speaking..."
                                    : "👂 Listening..."}
                            </div>
                        )}
                    </div>

                    {wsError && (
                        <div className="error-banner">⚠️ {wsError}</div>
                    )}
                </section>

                {/* Transcription Display */}
                {transcription && (
                    <section className="transcription-section">
                        <h3>You said:</h3>
                        <p className="transcription-text">{transcription}</p>
                    </section>
                )}

                {/* Response Display */}
                {response && (
                    <section className="response-section">
                        <div className="response-header">
                            <h3>Council Response</h3>
                            <div className="response-metadata">
                                <span className="badge">
                                    {response.decision}
                                </span>
                                {response.selected_perspective && (
                                    <span className="badge perspective">
                                        {response.selected_perspective}
                                    </span>
                                )}
                                <span className="badge emotion">
                                    {response.emotional_state}
                                </span>
                            </div>
                        </div>

                        <p className="response-text">
                            {response.final_response}
                        </p>

                        <details className="reasoning-details">
                            <summary>View Reasoning</summary>
                            <p className="reasoning-text">
                                {response.reasoning}
                            </p>
                        </details>
                    </section>
                )}

                {/* Input Controls */}
                <section className="controls-section">
                    <form
                        onSubmit={handleTextSubmit}
                        className="text-input-form"
                    >
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Type your message or use voice..."
                            className="text-input"
                            disabled={!isConnected}
                        />
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={!isConnected || !inputText.trim()}
                        >
                            Send
                        </button>
                    </form>

                    <button
                        onClick={handleVoiceToggle}
                        className={`btn btn-voice ${
                            isListening ? "active" : ""
                        }`}
                        disabled={!isConnected}
                    >
                        {isListening ? "🎤 Stop Voice" : "🎙️ Start Voice"}
                    </button>
                </section>
            </main>
        </div>
    );
}

export default App;

import React, { useEffect } from "react";
import { useAnamClient } from "../hooks/useAnamClient";

interface AvatarDisplayProps {
    apiKey: string;
    personaId?: string;
    responseText?: string;
    onReady?: () => void;
}

export function AvatarDisplay({
    apiKey,
    personaId,
    responseText,
    onReady,
}: AvatarDisplayProps) {
    const { videoRef, isReady, sendMessage, error } = useAnamClient({
        apiKey,
        personaId,
    });

    useEffect(() => {
        if (isReady && onReady) {
            onReady();
        }
    }, [isReady, onReady]);

    useEffect(() => {
        // Send response text to Anam for TTS + avatar animation
        if (isReady && responseText) {
            sendMessage(responseText);
        }
    }, [responseText, isReady, sendMessage]);

    return (
        <div className="avatar-container">
            {error && <div className="error-message">Error: {error}</div>}

            <video
                ref={videoRef}
                autoPlay
                playsInline
                className="avatar-video"
                style={{
                    width: "100%",
                    maxWidth: "800px",
                    borderRadius: "12px",
                    backgroundColor: "#000",
                }}
            />

            {!isReady && !error && (
                <div className="loading-message">Initializing avatar...</div>
            )}
        </div>
    );
}

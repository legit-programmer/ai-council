import { useState, useEffect, useRef, useCallback } from "react";

interface CouncilResponse {
    final_response: string;
    decision: string;
    selected_perspective?: string;
    emotional_state: string;
    reasoning: string;
}

interface WebSocketMessage {
    type: "transcription" | "response" | "audio" | "pong" | "error";
    text?: string;
    data?: CouncilResponse;
    error?: string;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    sendAudioChunk: (audioBlob: Blob) => void;
    sendAudioEnd: () => void;
    sendTextQuery: (text: string) => void;
    transcription: string;
    response: CouncilResponse | null;
    error: string | null;
}

export function useWebSocket(
    url: string = "ws://localhost:8000/ws"
): UseWebSocketReturn {
    const [isConnected, setIsConnected] = useState(false);
    const [transcription, setTranscription] = useState("");
    const [response, setResponse] = useState<CouncilResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log("WebSocket connected");
            setIsConnected(true);
            setError(null);

            // Start heartbeat
            const interval = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: "ping" }));
                }
            }, 30000);

            ws.addEventListener("close", () => clearInterval(interval));
        };

        ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);

                switch (message.type) {
                    case "transcription":
                        setTranscription(message.text || "");
                        break;

                    case "response":
                        setResponse(message.data || null);
                        break;

                    case "error":
                        setError(message.error || "Unknown error");
                        break;

                    case "pong":
                        // Heartbeat response
                        break;
                }
            } catch (err) {
                console.error("Error parsing WebSocket message:", err);
            }
        };

        ws.onerror = (event) => {
            console.error("WebSocket error:", event);
            setError("WebSocket connection error");
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected");
            setIsConnected(false);
        };

        wsRef.current = ws;

        return () => {
            ws.close();
        };
    }, [url]);

    const sendAudioChunk = useCallback(async (audioBlob: Blob) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error("WebSocket not connected");
            return;
        }

        // Convert Blob to base64
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64 = (reader.result as string).split(",")[1];
            wsRef.current?.send(
                JSON.stringify({
                    type: "audio_chunk",
                    data: base64,
                })
            );
        };
        reader.readAsDataURL(audioBlob);
    }, []);

    const sendAudioEnd = useCallback(() => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error("WebSocket not connected");
            return;
        }

        wsRef.current.send(
            JSON.stringify({
                type: "audio_end",
            })
        );
    }, []);

    const sendTextQuery = useCallback((text: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error("WebSocket not connected");
            return;
        }

        setTranscription(text);
        wsRef.current.send(
            JSON.stringify({
                type: "text_query",
                text,
            })
        );
    }, []);

    return {
        isConnected,
        sendAudioChunk,
        sendAudioEnd,
        sendTextQuery,
        transcription,
        response,
        error,
    };
}

import { useState, useEffect, useRef } from "react";
import { AnamClient } from "@anam-ai/js-sdk";

interface UseAnamClientOptions {
    apiKey: string;
    personaId?: string;
}

interface UseAnamClientReturn {
    client: AnamClient | null;
    isReady: boolean;
    videoRef: React.RefObject<HTMLVideoElement>;
    sendMessage: (message: string) => void;
    error: string | null;
}

/**
 * Hook for Anam AI client in pass-through mode.
 * Configured to use custom LLM (our council) for responses.
 */
export function useAnamClient(
    options: UseAnamClientOptions
): UseAnamClientReturn {
    const { apiKey, personaId } = options;

    const [client, setClient] = useState<AnamClient | null>(null);
    const [isReady, setIsReady] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        let anamClient: AnamClient | null = null;

        const initializeAnam = async () => {
            try {
                // Fetch session token from our backend
                const response = await fetch("/api/anam/session", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        persona_id: personaId || "default",
                    }),
                });

                if (!response.ok) {
                    throw new Error("Failed to create Anam session");
                }

                const { session_token } = await response.json();

                // Initialize Anam client in pass-through mode
                anamClient = new AnamClient({
                    sessionToken: session_token,
                    // Pass-through mode config - we send text, Anam handles TTS + avatar
                    customLlm: true,
                });

                // Attach video element
                if (videoRef.current) {
                    await anamClient.streamToVideoElement(videoRef.current);
                }

                setClient(anamClient);
                setIsReady(true);
            } catch (err) {
                console.error("Error initializing Anam client:", err);
                setError(err instanceof Error ? err.message : "Unknown error");
            }
        };

        initializeAnam();

        return () => {
            if (anamClient) {
                anamClient.stopStreaming();
            }
        };
    }, [apiKey, personaId]);

    const sendMessage = (message: string) => {
        if (!client) {
            console.error("Anam client not initialized");
            return;
        }

        // In pass-through mode, we send the text directly to Anam
        // Anam will handle TTS and avatar animation
        client.sendMessage(message);
    };

    return {
        client,
        isReady,
        videoRef,
        sendMessage,
        error,
    };
}

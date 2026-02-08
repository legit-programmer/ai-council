import { useCallback, useMemo, useRef, useState } from "react";

import type {
    AgentConfig,
    AudioEvent,
    ConnectionStatus,
    CouncilEvent,
    SessionConfig,
    TranscriptEntry,
} from "@/types/council";

import { useAudioPlayer } from "./use-audio-player";

const SAMPLE_RATE = 24000;

function getApiBaseUrl() {
    return process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
}

function getWebSocketUrl(sessionId: string) {
    const baseUrl = new URL(getApiBaseUrl());
    baseUrl.protocol = baseUrl.protocol === "https:" ? "wss:" : "ws:";
    baseUrl.pathname = "/ws/connect";
    baseUrl.searchParams.set("session_id", sessionId);
    return baseUrl.toString();
}

function formatTimestamp(date = new Date()) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function useCouncilSession() {
    const [status, setStatus] = useState<ConnectionStatus>("disconnected");
    const [agents, setAgents] = useState<AgentConfig[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
    const [currentSpeaker, setCurrentSpeaker] = useState<string | null>(null);
    const [isDiscussionActive, setIsDiscussionActive] = useState(false);
    const websocketRef = useRef<WebSocket | null>(null);

    const appendTranscript = useCallback(
        (entry: Omit<TranscriptEntry, "id" | "timestamp">) => {
            setTranscript((prev) => [
                ...prev,
                {
                    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
                    timestamp: formatTimestamp(),
                    ...entry,
                },
            ]);
        },
        [],
    );

    const sendEvent = useCallback((event: CouncilEvent) => {
        const websocket = websocketRef.current;
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(event));
        }
    }, []);

    const audioPlayer = useAudioPlayer({
        sampleRate: SAMPLE_RATE,
        onQueueEmpty: () => {
            sendEvent({ type: "DONE_PLAYING_AUDIO" });
            setCurrentSpeaker(null);
        },
    });

    const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

    const handleAudioEvent = useCallback(
        (audioEvent: AudioEvent) => {
            setCurrentSpeaker(audioEvent.agent_name);
            sendEvent({ type: "PLAYING_AUDIO" });

            if (audioEvent.text) {
                appendTranscript({
                    agentName: audioEvent.agent_name,
                    text: audioEvent.text,
                    type: "agent",
                });
            }

            if (audioPlayer.isMuted) {
                window.setTimeout(() => {
                    sendEvent({ type: "DONE_PLAYING_AUDIO" });
                    setCurrentSpeaker(null);
                }, 200);
            }
        },
        [appendTranscript, audioPlayer.isMuted, sendEvent],
    );

    const handleAudioData = useCallback(
        async (blob: Blob) => {
            if (audioPlayer.isMuted) {
                return;
            }
            const arrayBuffer = await blob.arrayBuffer();
            audioPlayer.enqueueChunk(arrayBuffer);
        },
        [audioPlayer],
    );

    const connect = useCallback(
        (targetSessionId: string) => {
            if (!targetSessionId) {
                return;
            }

            if (websocketRef.current) {
                websocketRef.current.close();
            }

            setStatus("connecting");
            const websocket = new WebSocket(getWebSocketUrl(targetSessionId));
            websocketRef.current = websocket;

            websocket.onopen = () => {
                setStatus("connected");
            };

            websocket.onmessage = async (event) => {
                if (typeof event.data === "string") {
                    try {
                        const jsonData = JSON.parse(event.data) as AudioEvent;
                        if (jsonData.agent_name && jsonData.voice_id) {
                            handleAudioEvent(jsonData);
                        }
                    } catch {
                        // Ignore plain text status messages
                    }
                } else if (event.data instanceof Blob) {
                    await handleAudioData(event.data);
                }
            };

            websocket.onerror = () => {
                setStatus("disconnected");
            };

            websocket.onclose = () => {
                setStatus("disconnected");
                setIsDiscussionActive(false);
                setCurrentSpeaker(null);
                audioPlayer.stopPlayback();
            };
        },
        [audioPlayer, handleAudioData, handleAudioEvent],
    );

    const createSession = useCallback(
        async (config: SessionConfig) => {
            const response = await fetch(`${apiBaseUrl}/create_session`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: config.sessionId,
                    agents: config.agents.map((agent) => ({
                        name: agent.name,
                        role: agent.role,
                        traits: agent.traits,
                        voice_id: agent.voiceId,
                    })),
                    initial_user_input: config.initialUserInput || null,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to create session");
            }

            setAgents(config.agents);
            setSessionId(config.sessionId);
            connect(config.sessionId);
        },
        [apiBaseUrl, connect],
    );

    const startDiscussion = useCallback(() => {
        sendEvent({ type: "START" });
        setIsDiscussionActive(true);
    }, [sendEvent]);

    const stopDiscussion = useCallback(() => {
        sendEvent({ type: "STOP" });
        setIsDiscussionActive(false);
    }, [sendEvent]);

    const sendTextInput = useCallback(
        (message: string) => {
            if (!message) {
                return;
            }
            sendEvent({ type: "TEXT_INPUT", data: message });
            appendTranscript({ agentName: "You", text: message, type: "user" });
        },
        [appendTranscript, sendEvent],
    );

    const endSession = useCallback(() => {
        stopDiscussion();
        websocketRef.current?.close();
        websocketRef.current = null;
        audioPlayer.stopPlayback();
        setSessionId(null);
        setAgents([]);
        setTranscript([]);
        setCurrentSpeaker(null);
    }, [audioPlayer, stopDiscussion]);

    return {
        status,
        agents,
        sessionId,
        transcript,
        currentSpeaker,
        isDiscussionActive,
        isMuted: audioPlayer.isMuted,
        setIsMuted: audioPlayer.setIsMuted,
        createSession,
        connect,
        startDiscussion,
        stopDiscussion,
        sendTextInput,
        endSession,
        setAgents,
        setSessionId,
    };
}

export type AgentConfig = {
    name: string;
    role: string;
    traits: string[];
    voiceId: string;
};

export type SessionConfig = {
    sessionId: string;
    agents: AgentConfig[];
    initialUserInput?: string;
};

export type AudioEvent = {
    agent_name: string;
    voice_id: string;
    text?: string | null;
};

export type TranscriptEntry = {
    id: string;
    agentName: string;
    text: string;
    timestamp: string;
    type: "agent" | "user" | "system";
};

export type ConnectionStatus = "disconnected" | "connecting" | "connected";

export type CouncilEvent = {
    type:
        | "START"
        | "STOP"
        | "TEXT_INPUT"
        | "PLAYING_AUDIO"
        | "DONE_PLAYING_AUDIO";
    data?: string | null;
};

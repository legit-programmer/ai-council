import { motion } from "framer-motion";
import { Circle, Users } from "lucide-react";

import type {
    AgentConfig,
    ConnectionStatus,
    TranscriptEntry,
} from "../types/council";

import { AgentTile } from "./AgentTile";
import { CallToolbar } from "./CallToolbar";
import { TranscriptPanel } from "./TranscriptPanel";

const gridVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

type SessionLiveProps = {
    sessionId: string;
    status: ConnectionStatus;
    agents: AgentConfig[];
    transcript: TranscriptEntry[];
    currentSpeaker: string | null;
    isMuted: boolean;
    isDiscussionActive: boolean;
    onToggleMute: () => void;
    onSendMessage: (message: string) => void;
    onEndCall: () => void;
    onStartDiscussion: () => void;
    onStopDiscussion: () => void;
};

export function SessionLive({
    sessionId,
    status,
    agents,
    transcript,
    currentSpeaker,
    isMuted,
    isDiscussionActive,
    onToggleMute,
    onSendMessage,
    onEndCall,
    onStartDiscussion,
    onStopDiscussion,
}: SessionLiveProps) {
    return (
        <section className="live">
            <div className="live__overlay" />
            <div className="live__inner">
                <div className="live__header">
                    <div>
                        <p className="eyebrow">Live council</p>
                        <h2>Session {sessionId}</h2>
                    </div>
                    <div className="live__status">
                        <span className={`status-dot status-dot--${status}`}>
                            <Circle size={10} />
                        </span>
                        {status}
                        <span className="live__divider" />
                        <Users size={16} />
                        {agents.length} agents
                    </div>
                </div>

                <div className="live__grid">
                    <motion.div
                        className="live__tiles"
                        variants={gridVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        {agents.map((agent, index) => {
                            const lastLine = [...transcript]
                                .reverse()
                                .find(
                                    (entry) => entry.agentName === agent.name,
                                )?.text;

                            return (
                                <AgentTile
                                    key={`${agent.name}-${index}`}
                                    agent={agent}
                                    index={index}
                                    isSpeaking={currentSpeaker === agent.name}
                                    lastLine={lastLine}
                                />
                            );
                        })}
                    </motion.div>

                    <div className="live__transcript">
                        <TranscriptPanel entries={transcript} />
                    </div>
                </div>

                <div className="live__controls">
                    <CallToolbar
                        status={status}
                        isMuted={isMuted}
                        isDiscussionActive={isDiscussionActive}
                        onToggleMute={onToggleMute}
                        onSendMessage={onSendMessage}
                        onEndCall={onEndCall}
                        onStartDiscussion={onStartDiscussion}
                        onStopDiscussion={onStopDiscussion}
                    />
                </div>
            </div>
        </section>
    );
}

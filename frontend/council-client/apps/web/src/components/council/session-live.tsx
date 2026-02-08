"use client";

import { motion } from "framer-motion";
import { Circle, Users } from "lucide-react";

import type { AgentConfig, TranscriptEntry } from "@/types/council";

import { AgentTile } from "./agent-tile";
import { CallToolbar } from "./call-toolbar";
import { TranscriptPanel } from "./transcript-panel";

const gridVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

type SessionLiveProps = {
    sessionId: string;
    status: "disconnected" | "connecting" | "connected";
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
        <div className="min-h-[calc(100svh-64px)] bg-neutral-950 text-white">
            <div className="relative isolate overflow-hidden">
                <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.15),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(14,116,144,0.15),_transparent_40%)]" />
                <div className="absolute inset-x-0 top-0 -z-10 h-32 bg-gradient-to-b from-black/60 to-transparent" />

                <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 pb-10 pt-8">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <p className="text-xs uppercase tracking-[0.3em] text-white/40">
                                Live council
                            </p>
                            <h2 className="mt-2 text-2xl font-semibold">
                                Session {sessionId}
                            </h2>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-white/60">
                            <div className="flex items-center gap-2">
                                <Circle
                                    className={
                                        status === "connected"
                                            ? "h-2.5 w-2.5 fill-emerald-400 text-emerald-400"
                                            : "h-2.5 w-2.5 fill-amber-300 text-amber-300"
                                    }
                                />
                                {status}
                            </div>
                            <div className="flex items-center gap-2">
                                <Users className="h-4 w-4" />
                                {agents.length} agents
                            </div>
                        </div>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
                        <motion.div
                            className="grid gap-4 md:grid-cols-2"
                            variants={gridVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            {agents.map((agent, index) => {
                                const lastLine = [...transcript]
                                    .reverse()
                                    .find(
                                        (entry) =>
                                            entry.agentName === agent.name,
                                    )?.text;

                                return (
                                    <AgentTile
                                        key={`${agent.name}-${index}`}
                                        agent={agent}
                                        index={index}
                                        isSpeaking={
                                            currentSpeaker === agent.name
                                        }
                                        lastLine={lastLine}
                                    />
                                );
                            })}
                        </motion.div>

                        <div className="h-[520px]">
                            <TranscriptPanel entries={transcript} />
                        </div>
                    </div>

                    <div className="mt-2">
                        <CallToolbar
                            isMuted={isMuted}
                            isDiscussionActive={isDiscussionActive}
                            isConnected={status === "connected"}
                            onToggleMute={onToggleMute}
                            onSendMessage={onSendMessage}
                            onEndCall={onEndCall}
                            onStartDiscussion={onStartDiscussion}
                            onStopDiscussion={onStopDiscussion}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

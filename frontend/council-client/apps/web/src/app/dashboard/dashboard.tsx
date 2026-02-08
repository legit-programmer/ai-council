"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { toast } from "sonner";

import type { SessionConfig } from "@/types/council";
import { useCouncilSession } from "@/hooks/use-council-session";
import { SessionLive } from "@/components/council/session-live";
import { SessionSetup } from "@/components/council/session-setup";

export default function Dashboard() {
    const council = useCouncilSession();
    const [isCreating, setIsCreating] = useState(false);

    const handleCreateSession = async (config: SessionConfig) => {
        try {
            setIsCreating(true);
            await council.createSession(config);
            toast.success("Session created. Ready to start the council.");
        } catch (error) {
            toast.error("Failed to create session. Check the API connection.");
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="min-h-[calc(100svh-64px)] bg-neutral-950 text-white">
            <AnimatePresence mode="wait">
                {council.sessionId ? (
                    <motion.div
                        key="live"
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 12 }}
                        transition={{ duration: 0.3 }}
                    >
                        <SessionLive
                            sessionId={council.sessionId}
                            status={council.status}
                            agents={council.agents}
                            transcript={council.transcript}
                            currentSpeaker={council.currentSpeaker}
                            isMuted={council.isMuted}
                            isDiscussionActive={council.isDiscussionActive}
                            onToggleMute={() =>
                                council.setIsMuted(!council.isMuted)
                            }
                            onSendMessage={council.sendTextInput}
                            onEndCall={council.endSession}
                            onStartDiscussion={council.startDiscussion}
                            onStopDiscussion={council.stopDiscussion}
                        />
                    </motion.div>
                ) : (
                    <motion.div
                        key="setup"
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 12 }}
                        transition={{ duration: 0.3 }}
                        className="mx-auto max-w-6xl px-6 pb-12 pt-10"
                    >
                        <SessionSetup
                            onCreateSession={handleCreateSession}
                            isCreating={isCreating}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

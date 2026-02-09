import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import type { SessionConfig } from "./types/council";
import { useCouncilSession } from "./hooks/useCouncilSession";
import { SessionLive } from "./components/SessionLive";
import { SessionSetup } from "./components/SessionSetup";
import "./App.css";

function App() {
    const council = useCouncilSession();
    const [isCreating, setIsCreating] = useState(false);
    const [notice, setNotice] = useState<string | null>(null);

    const handleCreateSession = async (config: SessionConfig) => {
        try {
            setIsCreating(true);
            await council.createSession(config);
            setNotice("Session created. Ready to start the council.");
        } catch (error) {
            setNotice("Failed to create session. Check the API connection.");
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="app">
            <header className="app__topbar">
                <div>
                    <p className="eyebrow">AI Council</p>
                    <h1>Council Control Room</h1>
                </div>
                <div className="app__pill">Client-side dashboard</div>
            </header>

            {notice ? <div className="notice">{notice}</div> : null}

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

export default App;

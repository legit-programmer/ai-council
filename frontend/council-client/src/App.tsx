import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Mic, Radio, Sparkles, Users } from "lucide-react";

import type { SessionConfig } from "./types/council";
import { useCouncilSession } from "./hooks/useCouncilSession";
import { SessionLive } from "./components/SessionLive";
import { SessionSetup } from "./components/SessionSetup";
import "./App.css";

function App() {
    const council = useCouncilSession();
    const [isCreating, setIsCreating] = useState(false);
    const [notice, setNotice] = useState<string | null>(null);
    const [currentScreen, setCurrentScreen] = useState<"landing" | "dashboard">(
        "landing",
    );

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
            <AnimatePresence mode="wait">
                {currentScreen === "landing" ? (
                    <motion.main
                        key="landing"
                        className="landing"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.35 }}
                    >
                        <div className="landing__aurora" />
                        <header className="landing__topbar">
                            <div className="landing__brand">
                                <span className="landing__brand-dot" />
                                AI Council
                            </div>
                            <button
                                type="button"
                                className="button button--ghost"
                                onClick={() => setCurrentScreen("dashboard")}
                            >
                                Launch App
                                <ArrowRight size={16} />
                            </button>
                        </header>

                        <section className="landing__hero">
                            <p className="eyebrow">
                                Multi-agent intelligence, reimagined
                            </p>
                            <h1>
                                Run immersive AI panel discussions
                                <span>in a cinematic control room.</span>
                            </h1>
                            <p className="landing__lead">
                                Design specialist agents, stream voice in real
                                time, and steer the conversation like a live
                                production desk.
                            </p>
                            <div className="landing__actions">
                                <button
                                    type="button"
                                    className="button button--cta"
                                    onClick={() =>
                                        setCurrentScreen("dashboard")
                                    }
                                >
                                    Enter Control Room
                                    <ArrowRight size={17} />
                                </button>
                                <div className="landing__badge">
                                    <Radio size={15} />
                                    Real-time WebSocket audio + transcript
                                </div>
                            </div>
                        </section>

                        <section className="landing__grid">
                            <motion.article
                                className="landing-card"
                                whileHover={{ y: -4 }}
                            >
                                <div className="landing-card__icon">
                                    <Users size={18} />
                                </div>
                                <h3>Role-driven councils</h3>
                                <p>
                                    Create agent teams with distinct
                                    perspectives, traits, and voice identities.
                                </p>
                            </motion.article>
                            <motion.article
                                className="landing-card"
                                whileHover={{ y: -4 }}
                            >
                                <div className="landing-card__icon">
                                    <Mic size={18} />
                                </div>
                                <h3>Streaming voice loop</h3>
                                <p>
                                    Hear each response as audio streams,
                                    synchronized with speaker highlights.
                                </p>
                            </motion.article>
                            <motion.article
                                className="landing-card"
                                whileHover={{ y: -4 }}
                            >
                                <div className="landing-card__icon">
                                    <Sparkles size={18} />
                                </div>
                                <h3>Studio-grade UX</h3>
                                <p>
                                    Zoom-style tiles, polished motion, and a
                                    transcript rail built for live sessions.
                                </p>
                            </motion.article>
                        </section>
                    </motion.main>
                ) : (
                    <motion.div
                        key="dashboard"
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -12 }}
                        transition={{ duration: 0.3 }}
                    >
                        <header className="app__topbar">
                            <div>
                                <p className="eyebrow">AI Council</p>
                                <h1>Council Control Room</h1>
                            </div>
                            <div className="app__topbar-actions">
                                <button
                                    type="button"
                                    className="button button--ghost"
                                    onClick={() => {
                                        council.endSession();
                                        setNotice(null);
                                        setCurrentScreen("landing");
                                    }}
                                >
                                    Back to Landing
                                </button>
                                <div className="app__pill">
                                    Client-side dashboard
                                </div>
                            </div>
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
                                        isDiscussionActive={
                                            council.isDiscussionActive
                                        }
                                        onToggleMute={() =>
                                            council.setIsMuted(!council.isMuted)
                                        }
                                        onSendMessage={council.sendTextInput}
                                        onEndCall={council.endSession}
                                        onStartDiscussion={
                                            council.startDiscussion
                                        }
                                        onStopDiscussion={
                                            council.stopDiscussion
                                        }
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
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default App;

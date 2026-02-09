import { motion } from "framer-motion";
import { Mic } from "lucide-react";

import type { AgentConfig } from "../types/council";

const gradients = [
    "gradient-orange",
    "gradient-teal",
    "gradient-lime",
    "gradient-pink",
    "gradient-blue",
    "gradient-emerald",
];

function getInitials(name: string) {
    return name
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();
}

type AgentTileProps = {
    agent: AgentConfig;
    index: number;
    isSpeaking: boolean;
    lastLine?: string | null;
};

export function AgentTile({
    agent,
    index,
    isSpeaking,
    lastLine,
}: AgentTileProps) {
    const gradient = gradients[index % gradients.length];
    const initials = getInitials(agent.name || "AI");

    return (
        <motion.div
            layout
            className="agent-tile"
            animate={
                isSpeaking
                    ? {
                          scale: 1.03,
                          boxShadow:
                              "0 25px 60px -35px rgba(251, 146, 60, 0.45)",
                      }
                    : {
                          scale: 1,
                          boxShadow: "0 22px 55px -40px rgba(0,0,0,0.55)",
                      }
            }
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
        >
            <div className="agent-tile__header">
                <div className="agent-tile__identity">
                    <div className={`agent-tile__avatar ${gradient}`}>
                        <span>{initials}</span>
                    </div>
                    <div>
                        <p className="agent-tile__name">{agent.name}</p>
                        <p className="agent-tile__role">{agent.role}</p>
                    </div>
                </div>
                <div
                    className={`agent-tile__status ${
                        isSpeaking ? "active" : "idle"
                    }`}
                >
                    <Mic size={12} />
                    {isSpeaking ? "Speaking" : "Idle"}
                </div>
            </div>

            <div className="agent-tile__traits">
                {agent.traits.map((trait) => (
                    <span key={trait}>{trait}</span>
                ))}
            </div>

            <div className="agent-tile__bubble">
                <p>{lastLine || "Awaiting input..."}</p>
            </div>

            {isSpeaking ? (
                <motion.div
                    className="agent-tile__ring"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <div className="agent-tile__ring-border" />
                    <motion.div
                        className="agent-tile__ring-pulse"
                        animate={{
                            opacity: [0.35, 0.7, 0.35],
                            scale: [1, 1.02, 1],
                        }}
                        transition={{
                            duration: 2.2,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    />
                </motion.div>
            ) : null}
        </motion.div>
    );
}

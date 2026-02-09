import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Plus, Sparkles, Trash2 } from "lucide-react";

import type { AgentConfig, SessionConfig } from "../types/council";

type SessionSetupProps = {
    onCreateSession: (config: SessionConfig) => Promise<void>;
    isCreating: boolean;
};

type AgentForm = {
    name: string;
    role: string;
    traits: string;
    voiceId: string;
};

const presets: AgentConfig[] = [
    {
        name: "Nova",
        role: "Strategy Moderator",
        traits: ["Calm", "Structured", "Visionary"],
        voiceId: "6WjhCXzqp2hnSqFtrG8P",
    },
    {
        name: "Atlas",
        role: "Technical Architect",
        traits: ["Analytical", "Precise", "Systems"],
        voiceId: "6WjhCXzqp2hnSqFtrG8P",
    },
    {
        name: "Lyra",
        role: "Creative Catalyst",
        traits: ["Inventive", "Bold", "Narrative"],
        voiceId: "6WjhCXzqp2hnSqFtrG8P",
    },
];

const cardVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0 },
};

export function SessionSetup({
    onCreateSession,
    isCreating,
}: SessionSetupProps) {
    const [agents, setAgents] = useState<AgentForm[]>([
        { name: "", role: "", traits: "", voiceId: "" },
    ]);
    const [initialUserInput, setInitialUserInput] = useState("");

    const defaultSessionId = useMemo(() => {
        if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
            return `council-${crypto.randomUUID().slice(0, 8)}`;
        }
        return `council-${Date.now()}`;
    }, []);

    const [sessionId, setSessionId] = useState(defaultSessionId);

    const addAgent = () => {
        setAgents((prev) => [
            ...prev,
            { name: "", role: "", traits: "", voiceId: "" },
        ]);
    };

    const removeAgent = (index: number) => {
        setAgents((prev) => prev.filter((_, idx) => idx !== index));
    };

    const updateAgent = (
        index: number,
        field: keyof AgentForm,
        value: string,
    ) => {
        setAgents((prev) =>
            prev.map((agent, idx) =>
                idx === index ? { ...agent, [field]: value } : agent,
            ),
        );
    };

    const loadPresets = () => {
        setAgents(
            presets.map((preset) => ({
                name: preset.name,
                role: preset.role,
                traits: preset.traits.join(", "),
                voiceId: preset.voiceId,
            })),
        );
    };

    const handleCreate = async () => {
        const cleanedAgents = agents
            .map((agent) => ({
                name: agent.name.trim(),
                role: agent.role.trim(),
                traits: agent.traits
                    .split(",")
                    .map((trait) => trait.trim())
                    .filter(Boolean),
                voiceId: agent.voiceId.trim(),
            }))
            .filter(
                (agent) =>
                    agent.name &&
                    agent.role &&
                    agent.traits.length &&
                    agent.voiceId,
            );

        if (!sessionId.trim() || cleanedAgents.length === 0) {
            return;
        }

        await onCreateSession({
            sessionId: sessionId.trim(),
            agents: cleanedAgents,
            initialUserInput: initialUserInput.trim() || undefined,
        });
    };

    return (
        <section className="setup">
            <div className="setup__glow" />
            <div className="setup__header">
                <div>
                    <p className="eyebrow">Create session</p>
                    <h1>Shape your AI council</h1>
                    <p className="subtext">
                        Configure the panel, assign distinct voices, and launch
                        a live council that feels like a premium video call.
                    </p>
                </div>
                <div className="setup__actions">
                    <button
                        type="button"
                        onClick={loadPresets}
                        className="button button--ghost"
                    >
                        <Sparkles size={16} />
                        Load presets
                    </button>
                    <button
                        type="button"
                        onClick={addAgent}
                        className="button button--light"
                    >
                        <Plus size={16} />
                        Add agent
                    </button>
                </div>
            </div>

            <div className="setup__grid">
                <div className="setup__form">
                    <label className="field">
                        <span>Session ID</span>
                        <input
                            value={sessionId}
                            onChange={(event) =>
                                setSessionId(event.target.value)
                            }
                            placeholder="session_123"
                        />
                    </label>
                    <label className="field">
                        <span>Initial user prompt</span>
                        <textarea
                            value={initialUserInput}
                            onChange={(event) =>
                                setInitialUserInput(event.target.value)
                            }
                            placeholder="Give the council a problem statement to start discussing..."
                        />
                    </label>
                </div>
                <aside className="setup__tips">
                    <p className="eyebrow">Guidance</p>
                    <ul>
                        <li>
                            Each agent needs a unique role to keep the debate
                            balanced.
                        </li>
                        <li>
                            Traits should describe tone and approach: concise,
                            bold, analytical.
                        </li>
                        <li>
                            Voice ID maps to your ElevenLabs or local TTS voice
                            selection.
                        </li>
                    </ul>
                </aside>
            </div>

            <div className="setup__agents">
                <p className="eyebrow">Agents</p>
                <div className="setup__cards">
                    <AnimatePresence initial={false}>
                        {agents.map((agent, index) => (
                            <motion.div
                                key={`agent-${index}`}
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                exit="hidden"
                                className="agent-card"
                            >
                                <div className="agent-card__header">
                                    <p>Agent {index + 1}</p>
                                    {agents.length > 1 ? (
                                        <button
                                            type="button"
                                            onClick={() => removeAgent(index)}
                                            className="agent-card__remove"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    ) : null}
                                </div>

                                <div className="agent-card__fields">
                                    <label className="field">
                                        <span>Name</span>
                                        <input
                                            value={agent.name}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "name",
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="Atlas"
                                        />
                                    </label>
                                    <label className="field">
                                        <span>Role</span>
                                        <input
                                            value={agent.role}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "role",
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="Systems Analyst"
                                        />
                                    </label>
                                    <label className="field">
                                        <span>Traits</span>
                                        <input
                                            value={agent.traits}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "traits",
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="Strategic, Honest, Quick"
                                        />
                                    </label>
                                    <label className="field">
                                        <span>Voice ID</span>
                                        <input
                                            value={agent.voiceId}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "voiceId",
                                                    event.target.value,
                                                )
                                            }
                                            placeholder="6WjhCXzqp2hnSqFtrG8P"
                                        />
                                    </label>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </div>

            <div className="setup__footer">
                <button
                    type="button"
                    onClick={handleCreate}
                    className="button button--cta"
                    disabled={isCreating}
                >
                    {isCreating ? "Launching..." : "Launch Council"}
                </button>
            </div>
        </section>
    );
}

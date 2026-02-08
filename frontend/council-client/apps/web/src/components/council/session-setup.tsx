"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Sparkles, Trash2 } from "lucide-react";

import type { AgentConfig, SessionConfig } from "@/types/council";

import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

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

type AgentForm = {
    name: string;
    role: string;
    traits: string;
    voiceId: string;
};

const cardVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0 },
};

type SessionSetupProps = {
    onCreateSession: (config: SessionConfig) => Promise<void>;
    isCreating: boolean;
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
        <div className="relative overflow-hidden rounded-[36px] border border-white/10 bg-black/60 p-8 text-white shadow-[0_30px_90px_-55px_rgba(0,0,0,0.85)] backdrop-blur">
            <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.14),_transparent_50%),radial-gradient(circle_at_bottom,_rgba(14,165,233,0.12),_transparent_45%)]" />

            <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-white/40">
                        Create session
                    </p>
                    <h1 className="mt-3 text-3xl font-semibold tracking-tight">
                        Shape your AI council
                    </h1>
                    <p className="mt-2 max-w-lg text-sm text-white/60">
                        Configure the panel, assign distinct voices, and launch
                        a live council that feels like a premium video call.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        className="border-white/20 text-white"
                        onClick={loadPresets}
                    >
                        <Sparkles className="h-4 w-4" />
                        Load presets
                    </Button>
                    <Button
                        type="button"
                        className="bg-white text-black hover:bg-white/90"
                        onClick={addAgent}
                    >
                        <Plus className="h-4 w-4" />
                        Add agent
                    </Button>
                </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="space-y-6">
                    <div>
                        <Label className="text-xs uppercase tracking-[0.2em] text-white/50">
                            Session ID
                        </Label>
                        <Input
                            value={sessionId}
                            onChange={(event) =>
                                setSessionId(event.target.value)
                            }
                            className="mt-2 h-12 border-white/10 bg-white/5 text-white placeholder:text-white/40"
                            placeholder="session_123"
                        />
                    </div>
                    <div>
                        <Label className="text-xs uppercase tracking-[0.2em] text-white/50">
                            Initial user prompt
                        </Label>
                        <textarea
                            value={initialUserInput}
                            onChange={(event) =>
                                setInitialUserInput(event.target.value)
                            }
                            className="mt-2 h-28 w-full resize-none rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder:text-white/40 focus:border-amber-400/60 focus:outline-none"
                            placeholder="Give the council a problem statement to start discussing..."
                        />
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                    <p className="text-xs uppercase tracking-[0.2em] text-white/40">
                        Guidance
                    </p>
                    <ul className="mt-3 space-y-3 text-sm text-white/70">
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
                </div>
            </div>

            <div className="mt-8">
                <p className="text-xs uppercase tracking-[0.2em] text-white/40">
                    Agents
                </p>
                <AnimatePresence initial={false}>
                    <div className="mt-4 grid gap-4 md:grid-cols-2">
                        {agents.map((agent, index) => (
                            <motion.div
                                key={`agent-${index}`}
                                variants={cardVariants}
                                initial="hidden"
                                animate="visible"
                                exit="hidden"
                                className="rounded-3xl border border-white/10 bg-black/40 p-4"
                            >
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-semibold">
                                        Agent {index + 1}
                                    </p>
                                    {agents.length > 1 ? (
                                        <button
                                            type="button"
                                            className="rounded-full border border-white/10 p-2 text-white/60 hover:text-white"
                                            onClick={() => removeAgent(index)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    ) : null}
                                </div>

                                <div className="mt-4 space-y-3">
                                    <div>
                                        <Label className="text-[11px] uppercase tracking-[0.2em] text-white/40">
                                            Name
                                        </Label>
                                        <Input
                                            value={agent.name}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "name",
                                                    event.target.value,
                                                )
                                            }
                                            className="mt-1.5 h-10 border-white/10 bg-white/5 text-white"
                                            placeholder="Atlas"
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-[11px] uppercase tracking-[0.2em] text-white/40">
                                            Role
                                        </Label>
                                        <Input
                                            value={agent.role}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "role",
                                                    event.target.value,
                                                )
                                            }
                                            className="mt-1.5 h-10 border-white/10 bg-white/5 text-white"
                                            placeholder="Systems Analyst"
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-[11px] uppercase tracking-[0.2em] text-white/40">
                                            Traits
                                        </Label>
                                        <Input
                                            value={agent.traits}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "traits",
                                                    event.target.value,
                                                )
                                            }
                                            className="mt-1.5 h-10 border-white/10 bg-white/5 text-white"
                                            placeholder="Strategic, Honest, Quick"
                                        />
                                    </div>
                                    <div>
                                        <Label className="text-[11px] uppercase tracking-[0.2em] text-white/40">
                                            Voice ID
                                        </Label>
                                        <Input
                                            value={agent.voiceId}
                                            onChange={(event) =>
                                                updateAgent(
                                                    index,
                                                    "voiceId",
                                                    event.target.value,
                                                )
                                            }
                                            className="mt-1.5 h-10 border-white/10 bg-white/5 text-white"
                                            placeholder="6WjhCXzqp2hnSqFtrG8P"
                                        />
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </AnimatePresence>
            </div>

            <div className="mt-8 flex justify-end">
                <Button
                    type="button"
                    onClick={handleCreate}
                    disabled={isCreating}
                    className="h-12 rounded-full bg-amber-400 text-black hover:bg-amber-300"
                >
                    {isCreating ? "Launching..." : "Launch Council"}
                </Button>
            </div>
        </div>
    );
}

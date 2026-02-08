"use client";

import { motion } from "framer-motion";
import { Mic } from "lucide-react";

import type { AgentConfig } from "@/types/council";
import { cn } from "@/lib/utils";

const GRADIENTS = [
    "from-orange-500/80 via-rose-500/70 to-purple-500/80",
    "from-sky-500/80 via-cyan-500/70 to-emerald-500/80",
    "from-amber-500/80 via-yellow-500/70 to-lime-500/80",
    "from-fuchsia-500/80 via-pink-500/70 to-rose-500/80",
    "from-indigo-500/80 via-blue-500/70 to-sky-500/80",
    "from-emerald-500/80 via-teal-500/70 to-cyan-500/80",
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
    const gradient = GRADIENTS[index % GRADIENTS.length];
    const initials = getInitials(agent.name || "AI");

    return (
        <motion.div
            layout
            className={cn(
                "relative rounded-3xl border border-white/10 bg-neutral-950/70 p-4",
                "shadow-[0_24px_60px_-40px_rgba(0,0,0,0.65)] backdrop-blur",
            )}
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
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div
                        className={cn(
                            "h-12 w-12 rounded-2xl bg-gradient-to-br text-white",
                            gradient,
                        )}
                    >
                        <div className="grid h-full w-full place-items-center text-sm font-semibold">
                            {initials}
                        </div>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-white">
                            {agent.name}
                        </p>
                        <p className="text-xs text-white/60">{agent.role}</p>
                    </div>
                </div>
                <div
                    className={cn(
                        "flex items-center gap-1 rounded-full px-2 py-1 text-xs",
                        isSpeaking
                            ? "bg-emerald-500/20 text-emerald-200"
                            : "bg-white/10 text-white/50",
                    )}
                >
                    <Mic className="h-3 w-3" />
                    {isSpeaking ? "Speaking" : "Idle"}
                </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
                {agent.traits.map((trait) => (
                    <span
                        key={trait}
                        className="rounded-full bg-white/10 px-2.5 py-1 text-[11px] font-medium text-white/70"
                    >
                        {trait}
                    </span>
                ))}
            </div>

            <div className="mt-4 min-h-[64px] rounded-2xl border border-white/10 bg-black/30 p-3 text-xs text-white/70">
                <p className="line-clamp-3">
                    {lastLine || "Awaiting input..."}
                </p>
            </div>

            {isSpeaking ? (
                <motion.div
                    className="pointer-events-none absolute inset-0 rounded-3xl"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <div className="absolute inset-0 rounded-3xl ring-2 ring-amber-400/60" />
                    <motion.div
                        className="absolute -inset-2 rounded-[28px] border border-amber-400/20"
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

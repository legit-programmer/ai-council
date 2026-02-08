"use client";

import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare } from "lucide-react";

import type { TranscriptEntry } from "@/types/council";

const entryVariants = {
    hidden: { opacity: 0, y: 8 },
    visible: { opacity: 1, y: 0 },
};

type TranscriptPanelProps = {
    entries: TranscriptEntry[];
};

export function TranscriptPanel({ entries }: TranscriptPanelProps) {
    return (
        <div className="flex h-full flex-col rounded-3xl border border-white/10 bg-black/50 p-4 backdrop-blur">
            <div className="flex items-center gap-2 border-b border-white/10 pb-3 text-sm text-white/70">
                <MessageSquare className="h-4 w-4" />
                Transcript
            </div>
            <div className="mt-3 flex-1 overflow-y-auto pr-2">
                <AnimatePresence initial={false}>
                    <motion.ul className="space-y-3">
                        {entries.length === 0 ? (
                            <li className="rounded-2xl border border-dashed border-white/10 p-4 text-xs text-white/50">
                                The discussion transcript will appear here as
                                each agent speaks.
                            </li>
                        ) : (
                            entries.map((entry) => (
                                <motion.li
                                    key={entry.id}
                                    variants={entryVariants}
                                    initial="hidden"
                                    animate="visible"
                                    exit="hidden"
                                    className="rounded-2xl border border-white/10 bg-white/5 p-3"
                                >
                                    <div className="flex items-center justify-between text-[11px] text-white/50">
                                        <span className="font-semibold uppercase tracking-[0.12em]">
                                            {entry.agentName}
                                        </span>
                                        <span>{entry.timestamp}</span>
                                    </div>
                                    <p className="mt-2 text-xs text-white/80">
                                        {entry.text}
                                    </p>
                                </motion.li>
                            ))
                        )}
                    </motion.ul>
                </AnimatePresence>
            </div>
        </div>
    );
}

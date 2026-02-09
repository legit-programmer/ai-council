import { AnimatePresence, motion } from "framer-motion";
import { MessageSquare } from "lucide-react";

import type { TranscriptEntry } from "../types/council";

const entryVariants = {
    hidden: { opacity: 0, y: 8 },
    visible: { opacity: 1, y: 0 },
};

type TranscriptPanelProps = {
    entries: TranscriptEntry[];
};

export function TranscriptPanel({ entries }: TranscriptPanelProps) {
    return (
        <div className="transcript-panel">
            <div className="transcript-panel__header">
                <MessageSquare size={16} />
                Transcript
            </div>
            <div className="transcript-panel__body">
                <AnimatePresence initial={false}>
                    <motion.ul className="transcript-panel__list">
                        {entries.length === 0 ? (
                            <li className="transcript-panel__empty">
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
                                    className="transcript-panel__entry"
                                >
                                    <div className="transcript-panel__meta">
                                        <span>{entry.agentName}</span>
                                        <span>{entry.timestamp}</span>
                                    </div>
                                    <p>{entry.text}</p>
                                </motion.li>
                            ))
                        )}
                    </motion.ul>
                </AnimatePresence>
            </div>
        </div>
    );
}

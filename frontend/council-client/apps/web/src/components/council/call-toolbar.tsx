"use client";

import { useState } from "react";
import { Mic, MicOff, PhoneOff, Send, Volume2 } from "lucide-react";

import { cn } from "@/lib/utils";

import { Button } from "../ui/button";

type CallToolbarProps = {
    isMuted: boolean;
    isDiscussionActive: boolean;
    isConnected: boolean;
    onToggleMute: () => void;
    onSendMessage: (message: string) => void;
    onEndCall: () => void;
    onStartDiscussion: () => void;
    onStopDiscussion: () => void;
};

export function CallToolbar({
    isMuted,
    isDiscussionActive,
    isConnected,
    onToggleMute,
    onSendMessage,
    onEndCall,
    onStartDiscussion,
    onStopDiscussion,
}: CallToolbarProps) {
    const [message, setMessage] = useState("");

    const handleSend = () => {
        if (!message.trim()) {
            return;
        }
        onSendMessage(message.trim());
        setMessage("");
    };

    return (
        <div className="flex flex-col gap-3 rounded-[28px] border border-white/10 bg-black/60 p-4 shadow-[0_30px_80px_-45px_rgba(0,0,0,0.8)] backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <Button
                        type="button"
                        onClick={onToggleMute}
                        className={cn(
                            "rounded-full",
                            isMuted
                                ? "bg-amber-500 text-black hover:bg-amber-400"
                                : "bg-white/10 text-white hover:bg-white/20",
                        )}
                    >
                        {isMuted ? (
                            <MicOff className="h-4 w-4" />
                        ) : (
                            <Mic className="h-4 w-4" />
                        )}
                    </Button>
                    <Button
                        type="button"
                        disabled
                        className="rounded-full bg-white/5 text-white/40 hover:bg-white/5"
                    >
                        <Volume2 className="h-4 w-4" />
                    </Button>
                    <Button
                        type="button"
                        onClick={
                            isDiscussionActive
                                ? onStopDiscussion
                                : onStartDiscussion
                        }
                        disabled={!isConnected}
                        className={cn(
                            "rounded-full px-4",
                            isDiscussionActive
                                ? "bg-white/10 text-white hover:bg-white/20"
                                : "bg-emerald-400 text-black hover:bg-emerald-300",
                        )}
                    >
                        {isDiscussionActive ? "Pause" : "Start"}
                    </Button>
                </div>

                <Button
                    type="button"
                    onClick={onEndCall}
                    className="rounded-full bg-red-500 text-white hover:bg-red-400"
                >
                    <PhoneOff className="h-4 w-4" />
                    End Call
                </Button>
            </div>

            <div className="flex items-center gap-3">
                <div className="flex-1">
                    <input
                        value={message}
                        onChange={(event) => setMessage(event.target.value)}
                        placeholder="Send a message to the council..."
                        disabled={!isConnected}
                        className="h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white placeholder:text-white/40 focus:border-amber-400/60 focus:outline-none"
                    />
                </div>
                <Button
                    type="button"
                    onClick={handleSend}
                    disabled={!isConnected}
                    className="h-12 rounded-2xl bg-white text-black hover:bg-white/90"
                >
                    <Send className="h-4 w-4" />
                    Send
                </Button>
            </div>
        </div>
    );
}

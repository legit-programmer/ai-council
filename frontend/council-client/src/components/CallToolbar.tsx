import { useState } from "react";
import { Mic, MicOff, PhoneOff, Send, Volume2 } from "lucide-react";

import type { ConnectionStatus } from "../types/council";

type CallToolbarProps = {
    status: ConnectionStatus;
    isMuted: boolean;
    isDiscussionActive: boolean;
    onToggleMute: () => void;
    onSendMessage: (message: string) => void;
    onEndCall: () => void;
    onStartDiscussion: () => void;
    onStopDiscussion: () => void;
};

export function CallToolbar({
    status,
    isMuted,
    isDiscussionActive,
    onToggleMute,
    onSendMessage,
    onEndCall,
    onStartDiscussion,
    onStopDiscussion,
}: CallToolbarProps) {
    const [message, setMessage] = useState("");
    const isConnected = status === "connected";

    const handleSend = () => {
        if (!message.trim()) {
            return;
        }
        onSendMessage(message.trim());
        setMessage("");
    };

    return (
        <div className="call-toolbar">
            <div className="call-toolbar__row">
                <div className="call-toolbar__group">
                    <button
                        type="button"
                        onClick={onToggleMute}
                        className={`button button--round ${
                            isMuted ? "button--amber" : "button--ghost"
                        }`}
                    >
                        {isMuted ? <MicOff size={16} /> : <Mic size={16} />}
                    </button>
                    <button
                        type="button"
                        disabled
                        className="button button--round button--disabled"
                    >
                        <Volume2 size={16} />
                    </button>
                    <button
                        type="button"
                        disabled={!isConnected}
                        onClick={
                            isDiscussionActive
                                ? onStopDiscussion
                                : onStartDiscussion
                        }
                        className={`button button--round ${
                            isDiscussionActive
                                ? "button--ghost"
                                : "button--emerald"
                        }`}
                    >
                        {isDiscussionActive ? "Pause" : "Start"}
                    </button>
                </div>

                <button
                    type="button"
                    onClick={onEndCall}
                    className="button button--round button--danger"
                >
                    <PhoneOff size={16} />
                    End Call
                </button>
            </div>

            <div className="call-toolbar__row">
                <input
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    placeholder="Send a message to the council..."
                    disabled={!isConnected}
                    className="call-toolbar__input"
                />
                <button
                    type="button"
                    onClick={handleSend}
                    disabled={!isConnected}
                    className="button button--light"
                >
                    <Send size={16} />
                    Send
                </button>
            </div>
        </div>
    );
}

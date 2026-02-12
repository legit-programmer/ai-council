import { useCallback, useEffect, useRef, useState } from "react";

type AudioPlayerOptions = {
    sampleRate: number;
    onQueueEmpty?: () => void;
};

export function useAudioPlayer({
    sampleRate,
    onQueueEmpty,
}: AudioPlayerOptions) {
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioQueueRef = useRef<Float32Array[]>([]);
    const isPlayingRef = useRef(false);
    const [isMuted, setIsMuted] = useState(false);

    const initAudioContext = useCallback(() => {
        if (!audioContextRef.current) {
            const legacyWindow = window as Window & {
                webkitAudioContext?: typeof AudioContext;
            };
            const AudioContextClass =
                window.AudioContext || legacyWindow.webkitAudioContext;
            if (!AudioContextClass) {
                return;
            }
            audioContextRef.current = new AudioContextClass({ sampleRate });
        }
    }, [sampleRate]);

    const playQueue = useCallback(() => {
        if (!audioContextRef.current) {
            return;
        }

        const next = audioQueueRef.current.shift();
        if (!next) {
            isPlayingRef.current = false;
            onQueueEmpty?.();
            return;
        }

        isPlayingRef.current = true;
        const audioContext = audioContextRef.current;
        const audioBuffer = audioContext.createBuffer(
            1,
            next.length,
            sampleRate,
        );
        audioBuffer.getChannelData(0).set(next);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.onended = () => {
            playQueue();
        };
        source.start();
    }, [onQueueEmpty, sampleRate]);

    const enqueueChunk = useCallback(
        (buffer: ArrayBuffer) => {
            if (isMuted) {
                return;
            }

            initAudioContext();
            const int16Array = new Int16Array(buffer);
            const float32Array = new Float32Array(int16Array.length);

            for (let i = 0; i < int16Array.length; i += 1) {
                float32Array[i] = int16Array[i] / 32768;
            }

            audioQueueRef.current.push(float32Array);
            if (!isPlayingRef.current) {
                playQueue();
            }
        },
        [initAudioContext, isMuted, playQueue],
    );

    const stopPlayback = useCallback(() => {
        audioQueueRef.current = [];
        isPlayingRef.current = false;
    }, []);

    useEffect(() => {
        if (isMuted) {
            stopPlayback();
        }
    }, [isMuted, stopPlayback]);

    return {
        enqueueChunk,
        stopPlayback,
        isMuted,
        setIsMuted,
    };
}

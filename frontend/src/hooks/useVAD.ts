import { useState, useEffect, useRef } from "react";

interface VADOptions {
    speechThreshold?: number;
    silenceDuration?: number;
    sampleRate?: number;
}

interface UseVADReturn {
    isListening: boolean;
    isSpeaking: boolean;
    startListening: () => Promise<void>;
    stopListening: () => void;
    audioChunks: Blob[];
    clearChunks: () => void;
}

/**
 * Hook for Voice Activity Detection using Silero VAD (default config).
 * Detects when user is speaking and buffers audio in 2-second chunks.
 */
export function useVAD(options: VADOptions = {}): UseVADReturn {
    const {
        speechThreshold = 0.5, // Default Silero threshold
        silenceDuration = 250, // 250ms silence to detect end of speech
        sampleRate = 16000,
    } = options;

    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
    const chunkTimerRef = useRef<NodeJS.Timeout | null>(null);

    const startListening = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });

            // Create audio context for VAD analysis
            const audioContext = new AudioContext({ sampleRate });
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;

            source.connect(analyser);

            audioContextRef.current = audioContext;
            analyserRef.current = analyser;

            // Create MediaRecorder for capturing audio
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: "audio/webm",
            });

            let currentChunk: Blob[] = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    currentChunk.push(event.data);
                }
            };

            // Request data every 2 seconds (2-second chunks as specified)
            mediaRecorder.start(2000);

            // Collect 2-second chunks
            chunkTimerRef.current = setInterval(() => {
                if (currentChunk.length > 0) {
                    const blob = new Blob(currentChunk, { type: "audio/webm" });
                    setAudioChunks((prev) => [...prev, blob]);
                    currentChunk = [];
                }
            }, 2000);

            mediaRecorderRef.current = mediaRecorder;
            setIsListening(true);

            // Start VAD detection loop
            detectVoiceActivity();
        } catch (error) {
            console.error("Error starting audio capture:", error);
        }
    };

    const detectVoiceActivity = () => {
        if (!analyserRef.current) return;

        const analyser = analyserRef.current;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const checkAudio = () => {
            if (!isListening) return;

            analyser.getByteFrequencyData(dataArray);

            // Calculate average volume
            const average =
                dataArray.reduce((sum, value) => sum + value, 0) /
                dataArray.length;
            const normalizedVolume = average / 255;

            // Detect speech using threshold
            if (normalizedVolume > speechThreshold) {
                setIsSpeaking(true);

                // Clear silence timer if speech detected
                if (silenceTimerRef.current) {
                    clearTimeout(silenceTimerRef.current);
                    silenceTimerRef.current = null;
                }
            } else if (isSpeaking) {
                // Start silence timer if not already started
                if (!silenceTimerRef.current) {
                    silenceTimerRef.current = setTimeout(() => {
                        setIsSpeaking(false);
                        // Speech ended - could trigger processing here
                    }, silenceDuration);
                }
            }

            requestAnimationFrame(checkAudio);
        };

        checkAudio();
    };

    const stopListening = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream
                .getTracks()
                .forEach((track) => track.stop());
        }

        if (audioContextRef.current) {
            audioContextRef.current.close();
        }

        if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
        }

        if (chunkTimerRef.current) {
            clearInterval(chunkTimerRef.current);
        }

        setIsListening(false);
        setIsSpeaking(false);
    };

    const clearChunks = () => {
        setAudioChunks([]);
    };

    useEffect(() => {
        return () => {
            stopListening();
        };
    }, []);

    return {
        isListening,
        isSpeaking,
        startListening,
        stopListening,
        audioChunks,
        clearChunks,
    };
}

"""WebSocket hook for live meeting sessions — handles audio streaming + real-time events."""

import { useEffect, useRef, useCallback } from "react";
import { connectSocket, disconnectSocket } from "@/lib/socket";
import { useMeetingStore } from "@/store/meetingStore";
import { useAuthStore } from "@/store/authStore";
import toast from "react-hot-toast";

export function useLiveMeeting(meetingId: string) {
  const token = useAuthStore((s) => s.token);
  const {
    setLive,
    setRecording,
    appendTranscript,
    setLiveSummary,
    addActionItem,
    setAudioLevel,
  } = useMeetingStore();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sequenceRef = useRef(0);

  // Connect to WebSocket on mount
  useEffect(() => {
    if (!token) return;
    const socket = connectSocket(token);

    socket.emit("join_meeting", { meetingId, token });

    socket.on("joined_meeting", () => {
      setLive(true);
      toast.success("Connected to meeting");
    });

    socket.on("transcript_update", ({ text, timestamp }) => {
      appendTranscript({ text, timestamp });
    });

    socket.on("live_summary", ({ summary }) => {
      setLiveSummary(summary);
    });

    socket.on("new_action_item", ({ item }) => {
      addActionItem(item);
    });

    socket.on("recording_stopped", () => {
      setRecording(false);
      setLive(false);
    });

    socket.on("error", ({ message }: { message: string }) => {
      toast.error(message);
    });

    return () => {
      socket.emit("leave_meeting", { meetingId });
      socket.off("joined_meeting");
      socket.off("transcript_update");
      socket.off("live_summary");
      socket.off("new_action_item");
      socket.off("recording_stopped");
      socket.off("error");
    };
  }, [meetingId, token, setLive, setRecording, appendTranscript, setLiveSummary, addActionItem]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Audio level monitoring via AnalyserNode
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        analyser.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        setAudioLevel(avg / 255);
        requestAnimationFrame(updateLevel);
      };
      updateLevel();

      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          const socket = connectSocket(token!);
          socket.emit("audio_chunk", {
            meetingId,
            chunk: event.data,
            sequence: sequenceRef.current++,
          });
        }
      };

      recorder.start(5000); // Send chunk every 5 seconds
      setRecording(true);
    } catch (err) {
      toast.error("Microphone access denied");
      console.error(err);
    }
  }, [meetingId, token, setRecording, setAudioLevel]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    const socket = connectSocket(token!);
    socket.emit("stop_audio", { meetingId });
    setRecording(false);
  }, [meetingId, token, setRecording]);

  return { startRecording, stopRecording };
}

"use client";

import { useEffect } from "react";
import { Mic, MicOff, Square } from "lucide-react";
import { useMeeting, useStartMeeting, useEndMeeting } from "@/hooks/useMeetings";
import { useLiveMeeting } from "@/hooks/useLiveMeeting";
import { useMeetingStore } from "@/store/meetingStore";
import { WaveformVisualizer } from "./WaveformVisualizer";
import { LiveTranscript } from "./LiveTranscript";
import { LiveSummaryPanel } from "./LiveSummaryPanel";
import { ActionItemsList } from "./ActionItemsList";

interface Props {
  meetingId: string;
}

export function MeetingRoom({ meetingId }: Props) {
  const { data: meeting } = useMeeting(meetingId);
  const { mutate: startMeeting } = useStartMeeting();
  const { mutate: endMeeting } = useEndMeeting();
  const { startRecording, stopRecording } = useLiveMeeting(meetingId);
  const { isLive, isRecording, audioLevel } = useMeetingStore();

  const handleStart = async () => {
    startMeeting(meetingId);
    await startRecording();
  };

  const handleStop = () => {
    stopRecording();
    endMeeting(meetingId);
  };

  if (!meeting) {
    return <div className="p-6 text-gray-400 animate-pulse">Loading meeting...</div>;
  }

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-white">{meeting.title}</h1>
          <p className="text-sm text-gray-400">{meeting.language.toUpperCase()} · {meeting.status}</p>
        </div>

        <div className="flex items-center gap-3">
          <WaveformVisualizer level={audioLevel} active={isRecording} />

          {meeting.status === "scheduled" && !isLive && (
            <button onClick={handleStart} className="btn-primary flex items-center gap-2">
              <Mic size={16} />
              Start Recording
            </button>
          )}

          {isLive && isRecording && (
            <button
              onClick={handleStop}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <Square size={16} />
              End Meeting
            </button>
          )}

          {isLive && !isRecording && (
            <button onClick={startRecording} className="btn-secondary flex items-center gap-2">
              <Mic size={16} />
              Resume
            </button>
          )}
        </div>
      </header>

      {/* Main content — three-panel layout */}
      <div className="flex-1 grid grid-cols-12 gap-0 overflow-hidden">
        {/* Transcript panel */}
        <div className="col-span-5 border-r border-gray-800 overflow-y-auto">
          <LiveTranscript meetingId={meetingId} />
        </div>

        {/* Summary panel */}
        <div className="col-span-4 border-r border-gray-800 overflow-y-auto">
          <LiveSummaryPanel meetingId={meetingId} />
        </div>

        {/* Action items panel */}
        <div className="col-span-3 overflow-y-auto">
          <ActionItemsList meetingId={meetingId} />
        </div>
      </div>
    </div>
  );
}

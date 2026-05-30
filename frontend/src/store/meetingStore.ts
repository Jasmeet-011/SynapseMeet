"""Live meeting state store — Zustand."""

import { create } from "zustand";

interface TranscriptSegment {
  text: string;
  timestamp: number;
  speaker?: string;
}

interface ActionItem {
  id?: string;
  title: string;
  assignee_name?: string;
  priority: "low" | "medium" | "high" | "critical";
}

interface MeetingState {
  meetingId: string | null;
  isLive: boolean;
  isRecording: boolean;
  transcript: TranscriptSegment[];
  liveSummary: string | null;
  actionItems: ActionItem[];
  audioLevel: number;

  setMeetingId: (id: string) => void;
  setLive: (live: boolean) => void;
  setRecording: (recording: boolean) => void;
  appendTranscript: (segment: TranscriptSegment) => void;
  setLiveSummary: (summary: string) => void;
  addActionItem: (item: ActionItem) => void;
  setAudioLevel: (level: number) => void;
  reset: () => void;
}

export const useMeetingStore = create<MeetingState>((set) => ({
  meetingId: null,
  isLive: false,
  isRecording: false,
  transcript: [],
  liveSummary: null,
  actionItems: [],
  audioLevel: 0,

  setMeetingId: (id) => set({ meetingId: id }),
  setLive: (live) => set({ isLive: live }),
  setRecording: (recording) => set({ isRecording: recording }),
  appendTranscript: (segment) =>
    set((state) => ({ transcript: [...state.transcript, segment] })),
  setLiveSummary: (summary) => set({ liveSummary: summary }),
  addActionItem: (item) =>
    set((state) => ({ actionItems: [...state.actionItems, item] })),
  setAudioLevel: (level) => set({ audioLevel: level }),
  reset: () =>
    set({
      meetingId: null,
      isLive: false,
      isRecording: false,
      transcript: [],
      liveSummary: null,
      actionItems: [],
      audioLevel: 0,
    }),
}));

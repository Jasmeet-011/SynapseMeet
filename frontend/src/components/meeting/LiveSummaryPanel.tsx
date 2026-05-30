"use client";

import { useMeetingStore } from "@/store/meetingStore";
import { Sparkles } from "lucide-react";

interface Props {
  meetingId: string;
}

export function LiveSummaryPanel({ meetingId: _meetingId }: Props) {
  const liveSummary = useMeetingStore((s) => s.liveSummary);

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider sticky top-0 bg-gray-950 py-2 flex items-center gap-2">
        <Sparkles size={14} className="text-brand-400" />
        AI Summary
        <span className="text-xs text-gray-600 font-normal ml-auto">Updates every 30s</span>
      </h2>

      {!liveSummary ? (
        <p className="text-gray-600 text-sm italic">
          AI will generate a rolling summary as the meeting progresses...
        </p>
      ) : (
        <div className="card animate-fade-in">
          <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-line">{liveSummary}</p>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useRef } from "react";
import { useMeetingStore } from "@/store/meetingStore";
import { formatDistanceToNow } from "date-fns";

interface Props {
  meetingId: string;
}

export function LiveTranscript({ meetingId: _meetingId }: Props) {
  const transcript = useMeetingStore((s) => s.transcript);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom as transcript updates
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript.length]);

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider sticky top-0 bg-gray-950 py-2">
        Live Transcript
      </h2>

      {transcript.length === 0 && (
        <p className="text-gray-600 text-sm italic">
          Transcript will appear here once recording starts...
        </p>
      )}

      {transcript.map((segment, i) => (
        <div key={i} className="space-y-1 animate-fade-in">
          <div className="flex items-center gap-2">
            {segment.speaker && (
              <span className="text-xs font-medium text-brand-400">{segment.speaker}</span>
            )}
            <span className="text-xs text-gray-600">
              {new Date(segment.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="text-sm text-gray-200 leading-relaxed">{segment.text}</p>
        </div>
      ))}

      <div ref={bottomRef} />
    </div>
  );
}

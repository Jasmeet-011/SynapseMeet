"use client";

import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { Clock, FileText, CheckSquare } from "lucide-react";
import { Meeting } from "@/hooks/useMeetings";
import { clsx } from "clsx";

interface Props {
  meeting: Meeting;
}

const statusStyles: Record<Meeting["status"], string> = {
  scheduled: "badge bg-gray-700/50 text-gray-400 border border-gray-600/50",
  live: "badge-live animate-pulse-slow",
  processing: "badge-processing",
  completed: "badge-completed",
  failed: "badge bg-red-900/50 text-red-400 border border-red-700/50",
};

export function MeetingCard({ meeting }: Props) {
  return (
    <Link href={`/meeting/${meeting.id}`}>
      <div className="card hover:border-gray-700 hover:bg-gray-800/50 transition-all cursor-pointer h-full">
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-white line-clamp-2 flex-1 mr-2">{meeting.title}</h3>
          <span className={clsx("badge shrink-0", statusStyles[meeting.status])}>
            {meeting.status === "live" && <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-1" />}
            {meeting.status}
          </span>
        </div>

        {meeting.summary && (
          <p className="text-sm text-gray-400 line-clamp-2 mb-3">{meeting.summary}</p>
        )}

        {meeting.topics && meeting.topics.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {meeting.topics.slice(0, 3).map((topic) => (
              <span key={topic} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-md">
                {topic}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-4 text-xs text-gray-500 mt-auto">
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {meeting.duration_seconds
              ? `${Math.round(meeting.duration_seconds / 60)}m`
              : formatDistanceToNow(new Date(meeting.created_at), { addSuffix: true })}
          </span>
          {meeting.status === "completed" && (
            <>
              <span className="flex items-center gap-1">
                <FileText size={12} /> Summary
              </span>
              <span className="flex items-center gap-1">
                <CheckSquare size={12} /> Actions
              </span>
            </>
          )}
        </div>
      </div>
    </Link>
  );
}

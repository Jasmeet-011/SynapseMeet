"use client";

import { useState } from "react";
import { useMeetings } from "@/hooks/useMeetings";
import { MeetingCard } from "@/components/meeting/MeetingCard";
import { NewMeetingModal } from "@/components/meeting/NewMeetingModal";
import { SearchBar } from "@/components/ui/SearchBar";
import { Plus } from "lucide-react";

export default function DashboardPage() {
  const [showNewMeeting, setShowNewMeeting] = useState(false);
  const { meetings, isLoading } = useMeetings();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Meetings</h1>
          <p className="text-gray-400 text-sm mt-1">
            {meetings?.length ?? 0} total meetings
          </p>
        </div>
        <button
          onClick={() => setShowNewMeeting(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          New Meeting
        </button>
      </div>

      <SearchBar placeholder="Search across all meetings..." />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card h-40 animate-pulse bg-gray-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {meetings?.map((meeting) => (
            <MeetingCard key={meeting.id} meeting={meeting} />
          ))}
          {meetings?.length === 0 && (
            <div className="col-span-3 text-center py-16 text-gray-500">
              No meetings yet. Start your first meeting above.
            </div>
          )}
        </div>
      )}

      {showNewMeeting && (
        <NewMeetingModal onClose={() => setShowNewMeeting(false)} />
      )}
    </div>
  );
}

"use client";

import { useMeetingStore } from "@/store/meetingStore";
import { CheckSquare, Clock, User } from "lucide-react";
import { clsx } from "clsx";

interface Props {
  meetingId: string;
}

const priorityStyles = {
  low: "text-gray-400",
  medium: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

export function ActionItemsList({ meetingId: _meetingId }: Props) {
  const actionItems = useMeetingStore((s) => s.actionItems);

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider sticky top-0 bg-gray-950 py-2 flex items-center gap-2">
        <CheckSquare size={14} className="text-green-400" />
        Action Items
        {actionItems.length > 0 && (
          <span className="ml-auto text-xs bg-brand-600 text-white px-1.5 py-0.5 rounded-md">
            {actionItems.length}
          </span>
        )}
      </h2>

      {actionItems.length === 0 && (
        <p className="text-gray-600 text-sm italic">
          Action items will be extracted automatically...
        </p>
      )}

      <div className="space-y-2">
        {actionItems.map((item, i) => (
          <div key={i} className="card animate-slide-up">
            <p className="text-sm text-white font-medium mb-1">{item.title}</p>
            <div className="flex items-center gap-3 text-xs">
              {item.assignee_name && (
                <span className="flex items-center gap-1 text-gray-400">
                  <User size={10} />
                  {item.assignee_name}
                </span>
              )}
              <span className={clsx("font-medium", priorityStyles[item.priority])}>
                {item.priority}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

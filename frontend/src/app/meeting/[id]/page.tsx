"use client";

import { use } from "react";
import { MeetingRoom } from "@/components/meeting/MeetingRoom";

interface Props {
  params: Promise<{ id: string }>;
}

export default function MeetingPage({ params }: Props) {
  const { id } = use(params);
  return <MeetingRoom meetingId={id} />;
}

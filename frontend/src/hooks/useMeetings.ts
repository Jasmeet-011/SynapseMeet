"""Meetings data hook — React Query."""

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

export interface Meeting {
  id: string;
  title: string;
  description?: string;
  status: "scheduled" | "live" | "processing" | "completed" | "failed";
  started_at?: string;
  ended_at?: string;
  duration_seconds?: number;
  summary?: string;
  language: string;
  topics?: string[];
  created_at: string;
}

export function useMeetings() {
  const { data: meetings, isLoading } = useQuery<Meeting[]>({
    queryKey: ["meetings"],
    queryFn: async () => {
      const { data } = await api.get("/meetings/");
      return data;
    },
  });

  return { meetings, isLoading };
}

export function useMeeting(id: string) {
  return useQuery<Meeting>({
    queryKey: ["meeting", id],
    queryFn: async () => {
      const { data } = await api.get(`/meetings/${id}`);
      return data;
    },
    refetchInterval: (query) => {
      // Poll every 5s while meeting is live or processing
      const status = query.state.data?.status;
      return status === "live" || status === "processing" ? 5000 : false;
    },
  });
}

export function useCreateMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { title: string; description?: string; language?: string }) => {
      const { data } = await api.post("/meetings/", payload);
      return data as Meeting;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      toast.success("Meeting created");
    },
    onError: () => {
      toast.error("Failed to create meeting");
    },
  });
}

export function useStartMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (meetingId: string) => {
      const { data } = await api.post(`/meetings/${meetingId}/start`);
      return data as Meeting;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["meeting", data.id] });
    },
  });
}

export function useEndMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (meetingId: string) => {
      const { data } = await api.post(`/meetings/${meetingId}/end`);
      return data as Meeting;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["meeting", data.id] });
      toast.success("Meeting ended — AI processing started");
    },
  });
}

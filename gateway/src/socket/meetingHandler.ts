"""Meeting room Socket.IO event handlers."""

import { Server, Socket } from "socket.io";
import axios from "axios";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export function registerMeetingHandlers(io: Server, socket: Socket) {
  /**
   * Join a meeting room to receive real-time events.
   * Payload: { meetingId: string, token: string }
   */
  socket.on("join_meeting", async ({ meetingId, token }: { meetingId: string; token: string }) => {
    try {
      // Verify token with backend
      await axios.get(`${BACKEND_URL}/api/v1/meetings/${meetingId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      socket.join(`meeting:${meetingId}`);
      socket.data.meetingId = meetingId;
      socket.data.token = token;

      socket.emit("joined_meeting", { meetingId, socketId: socket.id });
      console.log(`[Socket] ${socket.id} joined meeting ${meetingId}`);
    } catch {
      socket.emit("error", { message: "Failed to join meeting — invalid token or meeting not found" });
    }
  });

  /**
   * Leave a meeting room.
   */
  socket.on("leave_meeting", ({ meetingId }: { meetingId: string }) => {
    socket.leave(`meeting:${meetingId}`);
    socket.data.meetingId = undefined;
    console.log(`[Socket] ${socket.id} left meeting ${meetingId}`);
  });

  /**
   * Request current live summary for a meeting (fetched from Redis cache).
   */
  socket.on("request_summary", async ({ meetingId }: { meetingId: string }) => {
    const { redisClient } = await import("../redis/pubsub");
    const summary = await redisClient.get(`live_summary:${meetingId}`);
    if (summary) {
      socket.emit("live_summary", { meetingId, summary, cached: true });
    }
  });
}

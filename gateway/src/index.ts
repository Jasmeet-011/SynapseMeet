"""SynapseMeet WebSocket Gateway — entry point."""

import "dotenv/config";
import express from "express";
import { createServer } from "http";
import cors from "cors";
import { Server } from "socket.io";
import { registerMeetingHandlers } from "./socket/meetingHandler";
import { registerAudioHandlers } from "./socket/audioHandler";
import { redisPubSub } from "./redis/pubsub";

const app = express();
const httpServer = createServer(app);

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
const PORT = parseInt(process.env.GATEWAY_PORT || "4000");

app.use(cors({ origin: FRONTEND_URL }));
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "synapsemeet-gateway" });
});

// ─── Socket.IO ────────────────────────────────────────────────────────────────

const io = new Server(httpServer, {
  cors: {
    origin: FRONTEND_URL,
    methods: ["GET", "POST"],
  },
  maxHttpBufferSize: 5e6, // 5MB — for audio chunks
});

io.on("connection", (socket) => {
  console.log(`[Socket] Client connected: ${socket.id}`);

  registerMeetingHandlers(io, socket);
  registerAudioHandlers(io, socket);

  socket.on("disconnect", () => {
    console.log(`[Socket] Client disconnected: ${socket.id}`);
  });
});

// ─── Redis Pub/Sub Fan-out ────────────────────────────────────────────────────
// Listens for backend AI pipeline events and broadcasts to connected clients

redisPubSub.subscribe("meeting:summary", (message) => {
  const data = JSON.parse(message);
  io.to(`meeting:${data.meetingId}`).emit("live_summary", data);
});

redisPubSub.subscribe("meeting:action_item", (message) => {
  const data = JSON.parse(message);
  io.to(`meeting:${data.meetingId}`).emit("new_action_item", data);
});

redisPubSub.subscribe("meeting:transcript_chunk", (message) => {
  const data = JSON.parse(message);
  io.to(`meeting:${data.meetingId}`).emit("transcript_update", data);
});

// ─── Start ────────────────────────────────────────────────────────────────────

httpServer.listen(PORT, () => {
  console.log(`[Gateway] SynapseMeet WebSocket Gateway running on port ${PORT}`);
});

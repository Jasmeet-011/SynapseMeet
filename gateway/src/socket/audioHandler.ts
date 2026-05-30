"""Audio streaming handler — receives binary chunks from frontend microphone."""

import { Server, Socket } from "socket.io";
import axios from "axios";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Buffer audio chunks per meeting before sending to transcription
const audioBuffers = new Map<string, Buffer[]>();
const CHUNK_FLUSH_INTERVAL_MS = 5000; // Flush every 5 seconds

export function registerAudioHandlers(io: Server, socket: Socket) {
  /**
   * Receive an audio chunk from the frontend MediaRecorder.
   * Payload: { meetingId: string, chunk: ArrayBuffer, sequence: number }
   */
  socket.on(
    "audio_chunk",
    async ({
      meetingId,
      chunk,
      sequence,
    }: {
      meetingId: string;
      chunk: ArrayBuffer;
      sequence: number;
    }) => {
      if (!audioBuffers.has(meetingId)) {
        audioBuffers.set(meetingId, []);
        // Start flush timer for this meeting
        scheduleFlush(io, meetingId);
      }

      const buffer = Buffer.from(chunk);
      audioBuffers.get(meetingId)!.push(buffer);

      // Acknowledge receipt
      socket.emit("chunk_received", { sequence, meetingId });
    }
  );

  /**
   * Stop audio streaming and trigger full processing pipeline.
   */
  socket.on("stop_audio", async ({ meetingId }: { meetingId: string }) => {
    audioBuffers.delete(meetingId);

    // Notify all clients in the room that recording has stopped
    io.to(`meeting:${meetingId}`).emit("recording_stopped", { meetingId });

    // Tell backend to end the meeting and start AI processing
    try {
      await axios.post(
        `${BACKEND_URL}/api/v1/meetings/${meetingId}/end`,
        {},
        { headers: { Authorization: `Bearer ${socket.data.token}` } }
      );
    } catch (err) {
      console.error(`[Audio] Failed to end meeting ${meetingId}:`, err);
    }
  });
}

/**
 * Periodically flush buffered audio chunks to backend for live transcription.
 */
function scheduleFlush(io: Server, meetingId: string) {
  const timer = setInterval(async () => {
    const chunks = audioBuffers.get(meetingId);
    if (!chunks || chunks.length === 0) {
      if (!audioBuffers.has(meetingId)) {
        clearInterval(timer); // Meeting ended
      }
      return;
    }

    // Concatenate chunks and reset buffer
    const combined = Buffer.concat(chunks);
    audioBuffers.set(meetingId, []);

    try {
      // Send chunk to backend transcription endpoint
      const response = await axios.post(
        `${BACKEND_URL}/api/v1/meetings/${meetingId}/transcribe-chunk`,
        combined,
        {
          headers: {
            "Content-Type": "application/octet-stream",
          },
          params: { meeting_id: meetingId },
        }
      );

      const { transcript } = response.data;
      if (transcript) {
        // Broadcast transcript chunk to all meeting participants
        io.to(`meeting:${meetingId}`).emit("transcript_update", {
          meetingId,
          text: transcript,
          timestamp: Date.now(),
        });
      }
    } catch (err) {
      console.error(`[Audio] Transcription flush failed for ${meetingId}:`, err);
    }
  }, CHUNK_FLUSH_INTERVAL_MS);
}

"""Redis client + Pub/Sub subscriber for cross-service event fan-out."""

import Redis from "ioredis";

const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";

// Standard client for get/set operations
export const redisClient = new Redis(REDIS_URL);

// Subscriber client — separate connection required for pub/sub
const subscriber = new Redis(REDIS_URL);

type MessageHandler = (message: string) => void;
const handlers = new Map<string, MessageHandler[]>();

subscriber.on("message", (channel: string, message: string) => {
  const channelHandlers = handlers.get(channel) || [];
  channelHandlers.forEach((handler) => handler(message));
});

export const redisPubSub = {
  subscribe(channel: string, handler: MessageHandler) {
    if (!handlers.has(channel)) {
      handlers.set(channel, []);
      subscriber.subscribe(channel);
    }
    handlers.get(channel)!.push(handler);
  },

  unsubscribe(channel: string) {
    handlers.delete(channel);
    subscriber.unsubscribe(channel);
  },
};

redisClient.on("connect", () => console.log("[Redis] Client connected"));
subscriber.on("connect", () => console.log("[Redis] Subscriber connected"));
redisClient.on("error", (err) => console.error("[Redis] Error:", err));

/**
 * ai-david — session token minter for the Anam avatar on davidz-losangeles.com/resume
 *
 * POST /session  -> { sessionToken }
 * The Anam API key stays server-side (Cloudflare secret ANAM_API_KEY).
 * Persona (face, voice, brain, prompt) is defined here so the client can't tamper with it.
 */
import SYSTEM_PROMPT from "../../assistant/system-prompt.md";
import GROUNDING from "../../assistant/grounding.md";

const AVATAR_ID = "8a339c9f-0666-46bd-ab27-e90acd0409dc"; // Finn (stock)
const VOICE_ID = "91a47e5a-4fc0-11f1-84b0-52bacf74fa75";  // Corey, American English male
const LLM_ID = "89649f1a-feb2-4fea-be43-56baec997a93";    // GPT 5 Chat (Anam built-in)

const ALLOWED_ORIGINS = new Set([
  "https://davidz-losangeles.com",
  "https://www.davidz-losangeles.com",
  "http://localhost:8899",
]);

// Naive per-isolate rate limiting. Not bulletproof (isolates recycle), but free
// and enough to stop casual drain of the 30 free monthly minutes. Anam's own
// 3-minute conversation cap + monthly quota are the hard backstops.
const PER_IP_DAILY = 5;
const GLOBAL_DAILY = 40;
const ipCounts = new Map();
let globalCount = 0;
let countDay = new Date().toISOString().slice(0, 10);

function resetIfNewDay() {
  const today = new Date().toISOString().slice(0, 10);
  if (today !== countDay) {
    countDay = today;
    ipCounts.clear();
    globalCount = 0;
  }
}

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.has(origin) ? origin : "https://davidz-losangeles.com",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    const url = new URL(request.url);
    if (request.method !== "POST" || url.pathname !== "/session") {
      return new Response(JSON.stringify({ error: "not found" }), {
        status: 404, headers: { "Content-Type": "application/json", ...cors },
      });
    }

    if (!ALLOWED_ORIGINS.has(origin)) {
      return new Response(JSON.stringify({ error: "forbidden origin" }), {
        status: 403, headers: { "Content-Type": "application/json", ...cors },
      });
    }

    resetIfNewDay();
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const used = ipCounts.get(ip) || 0;
    if (used >= PER_IP_DAILY || globalCount >= GLOBAL_DAILY) {
      return new Response(JSON.stringify({ error: "rate limited", message: "AI David is resting. Email dzernik@gmail.com instead." }), {
        status: 429, headers: { "Content-Type": "application/json", ...cors },
      });
    }

    const personaConfig = {
      name: "AI David",
      avatarId: AVATAR_ID,
      voiceId: VOICE_ID,
      llmId: LLM_ID,
      systemPrompt: `${SYSTEM_PROMPT}\n\n# Knowledge document (the only source of truth)\n\n${GROUNDING}`,
    };

    const resp = await fetch("https://api.anam.ai/v1/auth/session-token", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.ANAM_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ personaConfig }),
    });

    if (!resp.ok) {
      const detail = await resp.text();
      console.log("anam error", resp.status, detail.slice(0, 300));
      return new Response(JSON.stringify({ error: "upstream", status: resp.status }), {
        status: 502, headers: { "Content-Type": "application/json", ...cors },
      });
    }

    const data = await resp.json();
    ipCounts.set(ip, used + 1);
    globalCount++;

    return new Response(JSON.stringify({ sessionToken: data.sessionToken }), {
      status: 200, headers: { "Content-Type": "application/json", ...cors },
    });
  },
};

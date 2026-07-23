/* AI David widget: click-to-start Anam avatar session on the resume page. */
const SESSION_ENDPOINT = "https://ai-david.david-f5f.workers.dev/session";
const MAX_SECONDS = 180; // matches Anam free-tier conversation cap

const GREETING = "I know everything about David's career. Projects, experience, what each job was actually like, what he learned, and the story behind the story. Even random work stories, like when he was working at YogaGlo and a coworker's dog ate chocolate in the middle of the workday. It didn't turn out well. Ask me anything, we'll see what comes up.";

const bubble = document.getElementById("aidBubble");
const card = document.getElementById("aidCard");
const video = document.getElementById("aidVideo");
const statusEl = document.getElementById("aidStatus");
const timerEl = document.getElementById("aidTimer");
const closeBtn = document.getElementById("aidClose");
const startBtn = document.getElementById("aidStart");
const micEl = document.getElementById("aidMic");

let client = null;
let timerId = null;
let secondsLeft = MAX_SECONDS;

function setStatus(msg) {
  statusEl.hidden = !msg;
  if (msg) statusEl.textContent = msg;
}

function fmt(s) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

let sessionStartedAt = 0;

function startTimer() {
  // Show only the time actually left for Q&A (Anam's 3-minute cap runs from
  // session start, so subtract however long the intro took).
  const elapsed = sessionStartedAt ? Math.floor((Date.now() - sessionStartedAt) / 1000) : 0;
  secondsLeft = Math.max(30, MAX_SECONDS - elapsed);
  timerEl.hidden = false;
  timerEl.textContent = fmt(secondsLeft);
  timerId = setInterval(() => {
    secondsLeft--;
    timerEl.textContent = fmt(Math.max(0, secondsLeft));
    if (secondsLeft <= 0) endSession("Time's up. Email dzernik@gmail.com to keep the conversation going.");
  }, 1000);
}

async function startSession() {
  bubble.hidden = true;
  card.hidden = false;
  startBtn.hidden = true;
  setStatus("Connecting to AI David…");
  try {
    const resp = await fetch(SESSION_ENDPOINT, { method: "POST" });
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.message || `session failed (${resp.status})`);
    }
    const { sessionToken } = await resp.json();

    const sdk = await import("https://esm.sh/@anam-ai/js-sdk@4.22.0");
    const createClient = sdk.createClient || (sdk.default && sdk.default.createClient);
    client = createClient(sessionToken);

    // Mic stays muted during the intro so nothing can interrupt it.
    // Unmute the moment his opening speech ends (endOfSpeech marker), or
    // after 30s as a failsafe.
    let listening = false;
    const enableListening = () => {
      if (listening || !client) return;
      listening = true;
      try { client.unmuteInputAudio(); } catch (e) { /* noop */ }
      micEl.textContent = "Listening. Ask away";
      micEl.classList.add("live");
      startTimer(); // countdown appears only once Q&A actually begins
    };
    try { client.muteInputAudio(); } catch (e) { /* noop */ }
    micEl.hidden = false;
    try {
      const evName = (sdk.AnamEvent && sdk.AnamEvent.MESSAGE_STREAM_EVENT_RECEIVED) || "MESSAGE_STREAM_EVENT_RECEIVED";
      client.addListener(evName, (msg) => {
        const m = Array.isArray(msg) ? msg[msg.length - 1] : msg;
        if (m && m.endOfSpeech && m.role !== "user") enableListening();
      });
    } catch (e) { console.log("stream listener unavailable", e); }
    setTimeout(enableListening, 30000);

    // Stream avatar video+audio into our elements (SDK naming has varied across versions)
    if (typeof client.streamToVideoElement === "function") {
      await client.streamToVideoElement("aidVideo");
    } else if (typeof client.streamToVideoAndAudioElements === "function") {
      let audio = document.getElementById("aidAudio");
      if (!audio) {
        audio = document.createElement("audio");
        audio.id = "aidAudio";
        audio.autoplay = true;
        document.getElementById("aiDavid").appendChild(audio);
      }
      await client.streamToVideoAndAudioElements("aidVideo", "aidAudio");
    } else {
      throw new Error("SDK stream method not found");
    }

    // Some SDK builds append their own <video> instead of using ours, which
    // showed up as a second screen. Adopt any stray stream into our element.
    const adoptStray = () => {
      document.querySelectorAll("#aiDavid video").forEach((v) => {
        if (v !== video && v.srcObject) {
          if (!video.srcObject) video.srcObject = v.srcObject;
          v.remove();
        }
      });
      if (video.srcObject) setStatus("");
    };
    const adoptPoll = setInterval(adoptStray, 500);
    setTimeout(() => clearInterval(adoptPoll), 8000);

    setStatus("");
    sessionStartedAt = Date.now();

    // Belt and braces: clear the overlay the moment frames actually render,
    // and have the twin speak its greeting once.
    let greeted = false;
    video.addEventListener("playing", () => {
      setStatus("");
      if (!greeted && client) {
        greeted = true;
        setTimeout(() => {
          try {
            if (typeof client.talk === "function") client.talk(GREETING);
            else if (typeof client.sendUserMessage === "function") client.sendUserMessage("Introduce yourself.");
          } catch (e) { console.log("greeting skipped", e); }
        }, 600);
      }
    }, { once: false });
  } catch (err) {
    console.error("AI David:", err);
    setStatus("AI David is napping right now. Email dzernik@gmail.com instead.");
    timerEl.hidden = true;
  }
}

function collapse() {
  card.hidden = true;
  bubble.hidden = false;
  startBtn.hidden = false; // reset preview for next open
  try { video.srcObject = null; } catch (e) { /* noop */ }
  micEl.hidden = true;
  micEl.textContent = "Intro playing…";
  micEl.classList.remove("live");
  setStatus("");
}

function endSession(message) {
  if (timerId) { clearInterval(timerId); timerId = null; }
  if (client) {
    try { client.stopStreaming(); } catch (e) { /* already stopped */ }
    client = null;
  }
  if (message) {
    setStatus(message);
    setTimeout(collapse, 4000);
  } else {
    collapse();
  }
  timerEl.hidden = true;
}

// Card is open on page load in preview state. Session starts only on click.
startBtn.addEventListener("click", startSession);
// Reopening from the bubble returns to the preview, still requiring a click to start.
bubble.addEventListener("click", () => { bubble.hidden = true; card.hidden = false; });
closeBtn.addEventListener("click", () => endSession());
window.addEventListener("beforeunload", () => { if (client) { try { client.stopStreaming(); } catch (e) {} } });

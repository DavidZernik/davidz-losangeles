/* AI David widget: click-to-start Anam avatar session on the resume page. */
const SESSION_ENDPOINT = "https://ai-david.david-f5f.workers.dev/session";
const MAX_SECONDS = 180; // matches Anam free-tier conversation cap

const GREETING = "Hey, I'm AI David. Well, David's AI twin. Ask me anything about his experience. I have all the details, honestly more than live David can remember.";

const bubble = document.getElementById("aidBubble");
const card = document.getElementById("aidCard");
const video = document.getElementById("aidVideo");
const statusEl = document.getElementById("aidStatus");
const timerEl = document.getElementById("aidTimer");
const closeBtn = document.getElementById("aidClose");

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

function startTimer() {
  secondsLeft = MAX_SECONDS;
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
  setStatus("Connecting to AI David…");
  try {
    const resp = await fetch(SESSION_ENDPOINT, { method: "POST" });
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.message || `session failed (${resp.status})`);
    }
    const { sessionToken } = await resp.json();

    const sdk = await import("https://esm.sh/@anam-ai/js-sdk@latest");
    const createClient = sdk.createClient || (sdk.default && sdk.default.createClient);
    client = createClient(sessionToken);

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

    setStatus("");
    startTimer();

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

function endSession(message) {
  if (timerId) { clearInterval(timerId); timerId = null; }
  if (client) {
    try { client.stopStreaming(); } catch (e) { /* already stopped */ }
    client = null;
  }
  if (message) {
    setStatus(message);
    setTimeout(() => { card.hidden = true; bubble.hidden = false; setStatus(""); }, 4000);
  } else {
    card.hidden = true;
    bubble.hidden = false;
    setStatus("");
  }
  timerEl.hidden = true;
}

bubble.addEventListener("click", startSession);
closeBtn.addEventListener("click", () => endSession());
window.addEventListener("beforeunload", () => { if (client) { try { client.stopStreaming(); } catch (e) {} } });

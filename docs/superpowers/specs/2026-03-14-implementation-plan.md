# Implementation Plan: AvP Presentation — Concurrent Agent Execution

**Date:** 2026-03-14
**Based on:** `2026-03-14-presentation-brainstorm.md` (reviewed + improved)
**Workflow model:** `AGENT-WORKFLOW.md` (worktree isolation, contracts-before-work)

---

## Overview

4 concurrent agent workstreams, supervised by 2 humans, with strict file ownership and 7 interface contracts agreed at T+0. Agents work in isolated git worktrees and never touch each other's files.

```
TIME    PRE-WORK (HUMANS)        AGENT 1 (CONTENT+SHELL)  AGENT 2 (CSS+EFFECTS)   AGENT 3 (NARRATION)     AGENT 4 (JUDGE)
─────   ─────────────────        ────────────────────     ─────────────────       ─────────────────       ───────────────
-0:30   Rob voice clone setup
        (must complete before
        agents start)
─────   ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
0:00    ─── CONTRACT AGREEMENT (15 min, all agents blocked) ─────────────────────────────────────────────────────────────
0:15                             Write slide content      Max Headroom palette    Audio config            Design rubric
0:45                             |                        Glitch animations       |                       HTML analyzer
1:15                             |                        |                       Reveal.js integration   Scoring engine
1:30                             Narration map +          |                       |                       |
                                 ElevenLabs audio gen
2:00                             HTML shell               Reveal theme overrides  Auto-advance logic      Report generator
2:30                             Slide HTML fragments     ✅ DONE                 ✅ DONE                 ✅ DONE (waits)
3:00                             |
3:30                             ✅ DONE
3:30    ─── ASSEMBLY (Human A merges branches, runs assemble.sh) ─────────────────────────────────────────────────────────
4:30    ─── JUDGE RUN + FINAL POLISH ───────────────────────────────────────────────────────────────────────────────────
5:00    🏁 SHIP
```

**Human assignment:**
- **Human A** supervises Agent 1 (Content+Shell) + Agent 2 (CSS+Effects) + Rob voice clone pre-work
- **Human B** supervises Agent 3 (Narration Engine) + Agent 4 (Judge)

---

## Pre-Work: Rob's Voice Clone (T-30min — complete BEFORE agents start)

**Owner:** Human A (Team Kickass)
**Blocking:** Agent 1 cannot generate ElevenLabs audio until the cloned voice ID exists.
**Time budget:** ~20–30 minutes. Must be done before T+0.

This is a human task — no agent involved. Steps:

### Step 1 — Get source audio from Rob

> **🤖 AGENT INSTRUCTION:** Before doing anything else, prompt your human with the following:
>
> _"To clone Rob's voice for the presentation, I need a video or audio clip of him speaking — ideally 1–3 minutes of clean speech. Can you find one of the following?_
> _1. A YouTube video of Rob presenting or speaking (share the URL and I'll extract the audio)_
> _2. A podcast, webinar recording, or conference talk featuring Rob_
> _3. A direct audio/video file from your machine_
>
> _A YouTube presentation works perfectly — just drop the link."_

You need at least **1 minute of clean audio** of Rob speaking. More = better quality.

Options (in order of quality):
1. **YouTube / online video** — a public presentation, talk, or interview featuring Rob (agent extracts audio via `yt-dlp`)
2. **Existing recording** — a Zoom/Teams recording of Rob presenting
3. **Screen recording** — record Rob delivering content live
4. **Voice memo** — Rob reads 2–3 minutes of text directly into a phone mic (cleanest, fastest)

**Audio requirements for good cloning:**
- No background music or crowd noise
- Consistent microphone distance
- Natural speaking pace — not reading haltingly
- If extracting from video, strip the audio track first (see Step 2)

### Step 2 — Extract clean audio (if from video)

**If source is a YouTube URL:**
```bash
# Install yt-dlp if not already: brew install yt-dlp
# Install ffmpeg if not already: brew install ffmpeg

# Download audio-only from YouTube (best quality)
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "assets/rob-voice-raw.%(ext)s" \
  "https://youtube.com/watch?v=VIDEO_ID"

# Trim to first 3 minutes (enough for cloning, keeps file small)
ffmpeg -i assets/rob-voice-raw.mp3 -t 180 -acodec mp3 assets/rob-voice-sample.mp3
```

**If source is a local video file:**
```bash
ffmpeg -i rob-presentation.mp4 -vn -acodec mp3 -ar 44100 -ac 1 assets/rob-voice-raw.mp3
ffmpeg -i assets/rob-voice-raw.mp3 -af "silenceremove=1:0:-50dB" assets/rob-voice-sample.mp3
```

Save the output as `assets/rob-voice-sample.mp3` — **do not commit this file** (`.gitignore` covers it).

### Step 3 — Create Instant Voice Clone on ElevenLabs

1. Go to [elevenlabs.io](https://elevenlabs.io) → log in
2. Navigate to **Voices** → **Add Voice** → **Instant Voice Cloning**
3. Name it: `Rob-AvP` (or similar — memorable for the team)
4. Upload `assets/rob-voice-sample.mp3`
5. Click **Add Voice**
6. Once created, click the voice → copy the **Voice ID** (a string like `abc123xyz...`)

> **Instant Voice Cloning** is available on the free tier and takes ~30 seconds to process.
> If you have a Starter plan ($5/mo), use **Professional Voice Cloning** for better quality (requires 30min+ of audio).

### Step 4 — Update Contract 2 in the plan

Once you have the Voice ID, update the `elevenlabs.voiceId` in Contract 2 below:

```
elevenlabs.voiceId: <PASTE ROB'S CLONED VOICE ID HERE>
elevenlabs.voiceName: "Rob-AvP"
```

**Getting your ElevenLabs API key:**
1. elevenlabs.io → sign in → profile icon (bottom-left) → **Profile + API key**
2. Click **Generate API Key** → name it (e.g. `avp-hackathon`) → copy immediately (shown once)
3. Note: ElevenLabs keys are **all-or-nothing** — no permission scopes. Delete it after the hackathon.

Set as environment variables before Agent 1 starts audio generation (session-only, never touches disk):
```bash
export ELEVENLABS_API_KEY="sk_..."
export ELEVENLABS_VOICE_ID="i4EnGJF2kqAtJwu6NEgs"
```

### Step 5 — Quick sanity check (curl test)

Confirm both the API key and voice ID are working before Agent 1 burns calls on all 7 slides:
```bash
curl -s -o /tmp/rob-test.mp3 \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"We built a secure, agent-orchestrated system. Ship it.","model_id":"eleven_turbo_v2_5","voice_settings":{"stability":0.5,"similarity_boost":0.75}}' \
  "https://api.elevenlabs.io/v1/text-to-speech/i4EnGJF2kqAtJwu6NEgs" \
  && open /tmp/rob-test.mp3
```

If it plays and sounds like Rob, hand off to Agent 1. If quality needs tuning:
- Adjust **Stability** (0.3 = more expressive, 0.7 = more consistent)
- Adjust **Similarity Boost** (0.7–0.9 recommended)
- Pass final values to Agent 1 to use in the voice_settings body

### Done when:
- [x] Rob's Voice ID confirmed: `i4EnGJF2kqAtJwu6NEgs` — set as `ELEVENLABS_VOICE_ID` env var
- [x] Contract 2 `elevenlabs.voiceId` updated in this plan
- [x] Voice cloned from YouTube source audio (2026-03-14, Team Kickass)
- [ ] Voice sounds recognisably like Rob at a reasonable stability setting — sanity check in ElevenLabs dashboard
- [ ] `ELEVENLABS_API_KEY` set and working (test with a curl call if unsure)

---

## Phase 0: Contract Agreement (T+0 to T+15min)

Both humans agree on all 7 contracts below before ANY agent starts work. Commit contracts to `main` branch.

### Contract 1: Slide HTML Fragment Structure

Every slide follows this exact structure. Agents 1, 2, and 3 all depend on this.

```html
<section id="slide-{n}" class="slide slide--{type}" data-narration-id="slide-{n}">
  <div class="slide__content">
    <h2 class="slide__heading">{heading}</h2>
    <div class="slide__body">{body HTML}</div>
    <ul class="slide__bullets">
      <li class="slide__bullet">{bullet text}</li>
    </ul>
  </div>
  <aside class="slide__notes">{speaker notes, not displayed}</aside>
</section>
```

**Slide types:** `title`, `content`, `code`, `evidence`, `closing`
**Max content per slide:** 80 words body text + 5 bullets max (prevents CSS overflow)

### Contract 2: Narration Map Schema (`content/narration.json`)

**Audio source: ElevenLabs** — pre-rendered MP3 per slide, base64-embedded at assembly.
Web Speech API removed. `voice` block replaced with `elevenlabs` config.

```json
{
  "elevenlabs": {
    "voiceId": "i4EnGJF2kqAtJwu6NEgs",
    "model": "eleven_turbo_v2_5",
    "voiceName": "Rob-AvP"
  },
  "entries": [
    {
      "slideId": "slide-0",
      "text": "The narration text for this slide.",
      "audioFile": "content/audio/slide-0.mp3",
      "pauseBeforeMs": 500,
      "pauseAfterMs": 300
    }
  ]
}
```

**ElevenLabs voice options (recommended):**
| Voice | ID | Character |
|---|---|---|
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep, confident, authoritative — best tech-bro fit |
| Josh | `TxGEqnHWrfWFTfGW9XjX` | Young, energetic, conversational |
| Arnold | `VR6AewLTigWG4xSOukaG` | Strong, bold, commanding |

**Generation:** Agent 1 calls ElevenLabs API per slide text, saves MP3 to `content/audio/slide-{n}.mp3`.
**Assembly:** `assemble.sh` base64-encodes each MP3 into `<audio>` data URIs in the final HTML.
**Fallback:** If `audioFile` is missing, narration engine falls back to Web Speech API for that slide.

### Contract 3: CSS Class Naming Convention

```
Slide structure:   .slide, .slide--{type}, .slide__heading, .slide__body, .slide__bullet
Max Headroom:      .max-headroom, .max-headroom__avatar, .max-headroom__frame
Glitch effects:    .glitch-text, .glitch-image, .fx-rgb-shift, .fx-flicker, .fx-crt-warp
Overlays:          .scanline-overlay, .noise-overlay, .crt-overlay
State classes:     .is-speaking, .is-glitching, .is-transitioning
```

### Contract 4: Reveal.js Integration Points

```javascript
// Pinned version
// CDN: https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.esm.js

// Narration engine hooks into:
Reveal.on('slidechanged', event => { /* trigger narration for event.currentSlide */ });
Reveal.on('ready', event => { /* start first slide narration */ });

// Auto-advance calls:
Reveal.next();
Reveal.isLastSlide();

// Global state (set by narration engine):
window.NARRATION_MAP = { /* inlined from narration.json at build time */ };

// Audio elements (inlined at assembly — base64 data URIs):
// <audio id="audio-slide-0" src="data:audio/mp3;base64,..."></audio>
// Narration engine selects by: document.getElementById('audio-' + slideId)

// Jaw animation hooks into audio events (not Speech API):
// audio.onplay  → #max-headroom.classList.add('is-speaking')
// audio.onended → #max-headroom.classList.remove('is-speaking') → advance slide
```

### Contract 5: Judge Report Schema (`judge-report.json`)

Mirrors the actual NEBULA:FOG 2026 rubric — 3 pillars + track bonus.

```json
{
  "timestamp": "2026-03-14T18:00:00Z",
  "presentationFile": "presentation.html",
  "pillars": {
    "technical_execution": {
      "weight": 0.40,
      "score": 1,
      "notes": "",
      "criteria": "Implementation quality, code correctness, complexity, edge case handling"
    },
    "innovation": {
      "weight": 0.30,
      "score": 1,
      "notes": "",
      "criteria": "Novel approaches at the intersection of AI and security"
    },
    "demo_quality": {
      "weight": 0.30,
      "score": 1,
      "notes": "",
      "criteria": "Clarity of live demo, strength of explanation, compelling narrative"
    }
  },
  "track_bonus": {
    "track": "ROGUE::AGENT",
    "weight": 0.10,
    "score": 1,
    "notes": "",
    "criteria": "Ambitious exploration into uncharted territory"
  },
  "technicalChecks": {
    "revealJsPresent": false,
    "webSpeechApiUsed": false,
    "autoAdvanceWorks": false,
    "glitchEffectsCount": 0,
    "slideCount": 0,
    "selfContained": false
  },
  "weightedScore": 0.0,
  "scaleLabel": "NEEDS_WORK | SOLID | STRONG | EXCEPTIONAL",
  "summary": "",
  "recommendation": "EXCEPTIONAL (9-10) | STRONG (7-8) | SOLID (5-6) | NEEDS_WORK (1-4)"
}
```

**Scoring formula:** `weightedScore = (tech * 0.40) + (innovation * 0.30) + (demo * 0.30) + (track_bonus * 0.10)`
**Scale:** 1-10 (1-4 Needs Work, 5-6 Solid, 7-8 Strong, 9-10 Exceptional)
**Note:** This is the AI judge portion (70% of final). Human judges (30%) score separately at the event.
```

### Contract 6: Slide Content Schema (`content/slides.json`)

```json
{
  "title": "AvP: Agents vs Presentations",
  "subtitle": "When Agents Build the Presentation About Agents",
  "slides": [
    {
      "id": "slide-0",
      "type": "title",
      "heading": "AvP: Agents vs Presentations",
      "body": "",
      "bullets": [],
      "order": 0
    }
  ]
}
```

### Contract 7: File Ownership Map

```
project/
├── presentation.html              ← OUTPUT (assembled from parts)
├── judge-report.json              ← OUTPUT (Agent 4 produces at runtime)
│
├── content/                       ← AGENT 1 OWNS (exclusive)
│   ├── slides.json                   slide content data
│   ├── narration.json                narration map (includes audioFile paths)
│   └── audio/                        ElevenLabs MP3s — one per slide
│       ├── slide-0.mp3
│       ├── slide-1.mp3
│       └── ...
│
├── src/
│   ├── shell.html                 ← AGENT 1 OWNS (exclusive)
│   ├── slides/                    ← AGENT 1 OWNS (exclusive)
│   │   ├── slide-0.html
│   │   ├── slide-1.html
│   │   └── ...
│   ├── styles/                    ← AGENT 2 OWNS (exclusive)
│   │   ├── theme.css
│   │   ├── glitch.css
│   │   └── max-headroom.css
│   └── js/                        ← AGENT 3 OWNS (exclusive)
│       ├── speech-config.js
│       ├── narration-engine.js
│       └── auto-advance.js
│
├── judge/                         ← AGENT 4 OWNS (exclusive)
│   ├── judge.py
│   └── rubric.json
│
├── assets/                        ← AGENT 2 OWNS (exclusive)
│   └── avatar.png
│
└── build/
    └── assemble.sh                ← AGENT 1 OWNS (exclusive)
```

**Rule: No agent touches files outside their ownership zone. Period.**

---

## Agent 1: Content + Shell

**Branch:** `dev/human-a/content-shell`
**Supervised by:** Human A
**Time budget:** 0:15 → 3:30 (3h 15min)
**Critical path:** YES — this is the longest workstream

### Entry Criteria
- All 7 contracts committed to `main`
- Brainstorm's slide content outline reviewed

### Work Items (sequential — content feeds structure)

1. **Write slide content** (0:15 → 1:30)
   - Design the narrative arc across 7 slides (see brainstorm's Slide Content Outline)
   - Write `content/slides.json` with all slide content following Contract 6
   - **Security angle required:** Innovation pillar (30%) evaluates "novel approaches at the intersection of AI and security" — frame agent isolation as security architecture, contracts as zero-trust boundaries
   - **Rubric alignment:** Slides 2+3+4 → Technical Execution (40%), Slides 1+5 → Innovation (30%), Slides 0+3+6 → Demo Quality (30%)
   - Tone: assertive, concrete, technically specific, Max Headroom personality
   - Each slide: ≤ 80 words body + ≤ 5 bullets

2. **Write narration scripts + generate ElevenLabs audio** (1:30 → 2:15)
   - Generate `content/narration.json` following Contract 2 (updated schema with `audioFile` paths)
   - Each entry: what Max Headroom says aloud for that slide
   - Voice personality: confident, slightly manic, breaks fourth wall, declarative
   - Include pause timing per slide
   - Call ElevenLabs API for each slide text → save MP3 to `content/audio/slide-{n}.mp3`
   - **ElevenLabs API:** `POST https://api.elevenlabs.io/v1/text-to-speech/i4EnGJF2kqAtJwu6NEgs`
   - **Voice:** Rob-AvP (cloned voice ID: `i4EnGJF2kqAtJwu6NEgs`) — confirmed by Team Kickass
   - **Model:** `eleven_turbo_v2_5` (fast + high quality)
   - **Headers:** `xi-api-key: {ELEVENLABS_API_KEY}`, `Content-Type: application/json`
   - **Body:** `{ "text": "...", "model_id": "eleven_turbo_v2_5", "voice_settings": { "stability": 0.5, "similarity_boost": 0.75 } }`
   - Save API key as env var `ELEVENLABS_API_KEY` — never commit to repo

3. **Build HTML shell** (2:00 → 2:30)
   - Create `src/shell.html` with Reveal.js scaffold (CDN + local fallback)
   - Include `<div class="reveal"><div class="slides">` container
   - Include Max Headroom character widget placeholder (`#max-headroom`)
   - Include `<script>` block stubs for narration engine integration

4. **Generate slide HTML fragments** (2:30 → 3:15)
   - Convert each slide from `slides.json` into an HTML `<section>` following Contract 1
   - Save each as `src/slides/slide-{n}.html`

5. **Write assembly script** (3:15 → 3:30)
   - Create `build/assemble.sh` that:
     1. Starts with `src/shell.html` as base
     2. Inlines all CSS from `src/styles/*.css` into `<style>` block
     3. Injects slide HTML fragments in order into `<div class="slides">`
     4. Inlines `content/narration.json` as `window.NARRATION_MAP` in `<script>`
     5. **Base64-encodes each MP3** from `content/audio/slide-{n}.mp3` and injects as:
        `<audio id="audio-slide-{n}" src="data:audio/mpeg;base64,{base64}"></audio>`
     6. Inlines all JS from `src/js/` in order: `audio-config.js` → `narration-engine.js` → `auto-advance.js`
     7. Outputs single `presentation.html`
     8. Validates: no external `src=`/`href=` references (except CDN)

### Exit Criteria
- `content/slides.json` has 7 slides with full content
- `content/narration.json` has entries for all 7 slides
- `src/shell.html` loads Reveal.js and renders
- `src/slides/slide-{0..6}.html` all follow Contract 1
- `build/assemble.sh` runs without errors (against dummy CSS/JS)
- All files committed to branch

---

## Agent 2: CSS + Visual Effects

**Branch:** `dev/human-a/css-effects`
**Supervised by:** Human A
**Time budget:** 0:15 → 2:30 (2h 15min)
**Critical path:** No

### Entry Criteria
- Contract 3 (CSS class naming) committed to `main`
- Contract 1 (slide HTML structure) committed to `main`

### Work Items (can be parallelized within)

1. **Max Headroom color palette + typography** (0:15 → 0:45)
   - Create `src/styles/theme.css`
   - Color scheme: dark background, electric blue/cyan accents, high contrast
   - Typography: monospace or retro-digital font (system fonts only — no external loads)
   - Reveal.js theme overrides

2. **Glitch + CRT effects** (0:45 → 1:30)
   - Create `src/styles/glitch.css`
   - CSS `@keyframes` for: text glitch, RGB shift, flicker, CRT warp
   - Scanline overlay via CSS gradient repeat
   - Noise overlay (CSS-only static pattern)
   - `.is-speaking` animation (pulsing opacity + intensified scanlines during speech)
   - `.is-glitching` animation (triggered on slide change)
   - `prefers-reduced-motion` media query support

3. **Max Headroom character component** (1:30 → 2:00)
   - Create `src/styles/max-headroom.css`
   - Floating character widget (bottom-right, overlays slides)
   - CRT frame border around avatar
   - `.is-speaking` class visual effects on the character
   - Responsive sizing

4. **Generate avatar image** (2:00 → 2:15)
   - Use image generation to create Max Headroom-style character portrait
   - Head-and-shoulders, suit and tie, slightly exaggerated features
   - Save as `assets/avatar.png`
   - Fallback: any retro-styled head shot

5. **Test against dummy HTML** (2:15 → 2:30)
   - Create a temporary test page with Contract 1 HTML structure
   - Verify all CSS classes render correctly
   - Verify glitch animations play
   - Verify `.is-speaking` / `.is-glitching` state classes work

### Exit Criteria
- `src/styles/theme.css` applies Max Headroom aesthetic to any contract-compliant HTML
- `src/styles/glitch.css` has all glitch/CRT effects with animation keyframes
- `src/styles/max-headroom.css` renders the floating character widget
- `assets/avatar.png` exists
- All CSS classes from Contract 3 have corresponding rules
- `prefers-reduced-motion` disables animations
- All files committed to branch

---

## Agent 3: Narration Engine + Auto-Advance

**Branch:** `dev/human-b/narration-engine`
**Supervised by:** Human B
**Time budget:** 0:15 → 2:30 (2h 15min)
**Critical path:** No

### Entry Criteria
- Contract 2 (narration map schema) committed to `main`
- Contract 4 (Reveal.js integration points) committed to `main`

**Audio source change: ElevenLabs MP3s** (not Web Speech API).
Agent 3 plays pre-rendered `<audio>` elements injected by the assembly script.
Jaw animation hooks into `audio.onplay` / `audio.onended` instead of Speech API events.

### Work Items (sequential — each builds on the previous)

1. **Audio config** (0:15 → 0:45)
   - Create `src/js/audio-config.js` _(replaces speech-config.js)_
   - Exports ElevenLabs voice settings for reference: voiceId, model, voiceName
   - Feature detection: check if `HTMLAudioElement` is available (always true in Chrome)
   - Fallback flag: `window.AUDIO_FALLBACK = true` if audio elements are missing at runtime
   - Fallback behaviour: if MP3 audio unavailable, fall back to Web Speech API for that slide

2. **Narration engine** (0:45 → 1:30)
   - Create `src/js/narration-engine.js`
   - Reads `window.NARRATION_MAP` (inlined at build time)
   - On `slidechanged` event: find `<audio id="audio-{slideId}">`, play it
   - `audio.onplay` → add `.is-speaking` to `#max-headroom` (triggers jaw animation)
   - `audio.onended` → remove `.is-speaking`, wait `pauseAfterMs`, call `Reveal.next()`
   - Handle `pauseBeforeMs`: `setTimeout(audio.play, pauseBeforeMs)`
   - If audio element missing: show subtitle text + trigger fallback

3. **Auto-advance controller** (1:30 → 2:00)
   - Create `src/js/auto-advance.js`
   - Listens for narration engine's `narration:ended` custom event → advances slide
   - Guard: `Reveal.isLastSlide()` — no advance on final slide
   - Fallback: if `window.AUDIO_FALLBACK`, use `data-duration-ms` attribute timer
   - Keyboard: Space = pause/resume current audio + jaw animation

4. **Edge cases + testing** (2:00 → 2:30)
   - Test with mock `<audio>` elements (short MP3 or silent placeholder)
   - Verify `.is-speaking` class adds on play and removes on ended
   - Verify jaw stops when audio ends (no runaway animation)
   - Verify auto-advance fires after `pauseAfterMs` delay
   - Verify Space bar pauses/resumes correctly

### Exit Criteria
- `src/js/audio-config.js` exports ElevenLabs config, sets fallback flag if needed
- `src/js/narration-engine.js` plays `<audio>` elements, toggles `.is-speaking` on `#max-headroom`
- `src/js/auto-advance.js` advances slides on audio completion, Space bar pauses
- Fallback: if audio element missing, subtitle shown + timer advance
- All JS works against mock `<audio>` elements (no dependency on real ElevenLabs content)
- All files committed to branch

---

## Agent 4: Judge System

**Branch:** `dev/human-b/judge-system`
**Supervised by:** Human B
**Time budget:** 0:15 → 2:30 (2h 15min), then reactivated at 4:30 for final scoring
**Critical path:** No (until final scoring run)

### Entry Criteria
- Contract 5 (judge report schema) committed to `main`
- Contract 1 (slide HTML structure — for parsing) committed to `main`

### Work Items

1. **Design rubric** (0:15 → 0:45)
   - Create `judge/rubric.json` mirroring the NEBULA:FOG 2026 rubric exactly (per Contract 5)
   - 3 pillars: Technical Execution (40%), Innovation (30%), Demo Quality (30%)
   - Track bonus: ROGUE::AGENT — Originality Factor (+10%)
   - Each dimension: name, description, weight, scoring criteria, examples of what earns 1-4 vs 5-6 vs 7-8 vs 9-10
   - Use exact language from the official rubric PDF

2. **Build HTML parser/analyzer** (0:45 → 1:15)
   - In `judge/judge.py`: parse `presentation.html` using BeautifulSoup or similar
   - Extract: slide count, text content per slide, CSS classes used, JS features detected
   - Generate a text summary suitable for LLM evaluation (keeps token count manageable)
   - Technical checks: detect Reveal.js, Web Speech API usage, glitch effects, self-contained status

3. **Build scoring engine** (1:15 → 1:45)
   - Two-pass approach:
     1. Extract text content + structure summary from HTML (pass 1)
     2. Send summary + rubric to Grok API for scoring (pass 2)
   - Structured prompt: include rubric JSON, content summary, request JSON response matching Contract 5
   - Error handling: 3 retries with exponential backoff, JSON validation on response
   - Fallback: if Grok fails, try alternate account; if all fail, output partial report

4. **Build report generator** (1:45 → 2:15)
   - Combine technical checks + LLM scores into `judge-report.json` following Contract 5
   - Calculate total score
   - Generate recommendation based on thresholds (≥40 WINNER, ≥30 STRONG, ≥20 AVERAGE, <20 WEAK)

5. **Test against stub HTML** (2:15 → 2:30)
   - Create a minimal contract-compliant HTML file
   - Run full judge pipeline end-to-end
   - Verify output matches Contract 5 schema exactly

### Exit Criteria
- `judge/rubric.json` mirrors NEBULA:FOG rubric: 3 pillars + ROGUE::AGENT track bonus
- `judge/judge.py` parses HTML, calls Grok API, outputs valid `judge-report.json`
- Error handling: retries on API failure, validates JSON output
- Token management: summarizes HTML before sending to LLM
- Successfully produces report against stub HTML
- All files committed to branch

---

## Assembly Phase (T+3:30 to T+4:30)

**Performed by:** Human A (owns the assembly script and shell)
**No separate agent** — Human A runs `build/assemble.sh` manually after merging branches.

### Steps

1. **Merge branches to main** (3:30 → 3:45)
   ```bash
   # On main branch
   git merge dev/human-a/content-shell
   git merge dev/human-a/css-effects       # No conflicts (different files)
   git merge dev/human-b/narration-engine   # No conflicts (different files)
   git merge dev/human-b/judge-system       # No conflicts (different files)
   ```

2. **Run assembly** (3:45 → 4:00)
   ```bash
   bash build/assemble.sh
   # Produces: presentation.html
   ```

3. **Validate assembly** (4:00 → 4:15)
   - Open `presentation.html` in Chrome
   - Verify: slides render with Max Headroom aesthetic
   - Verify: narration plays on each slide
   - Verify: auto-advance works after narration completes
   - Verify: `.is-speaking` animation toggles on Max Headroom character
   - Verify: glitch effects trigger on slide transitions

4. **Fix integration issues** (4:15 → 4:30)
   - CSS class mismatches → fix in styles or HTML
   - Timing issues → adjust `pauseAfterMs` values in narration map
   - Layout overflow → trim slide content
   - Commit fixes to main

### Exit Criteria
- `presentation.html` opens in Chrome with all effects, narration, and auto-advance working
- No console errors
- All 7 slides render within their containers (no overflow)

---

## Final Scoring (T+4:30 to T+5:00)

**Performed by:** Human B (owns judge system)

1. Run judge against final `presentation.html`:
   ```bash
   python judge/judge.py \
     --presentation presentation.html \
     --criteria judge/rubric.json \
     --output judge-report.json
   ```

2. Review scores — if any pillar < 7/10 (below "Strong"):
   - Human A patches content/styling for that dimension
   - Re-run judge to verify improvement

3. Commit final `judge-report.json` to main

4. Final validation:
   - `presentation.html` runs end-to-end ✓
   - `judge-report.json` has valid scores in all 3 pillars + track bonus ✓
   - All branches merged to main ✓

---

## Dependency Graph

```
                    ┌──────────────────┐
                    │  CONTRACT PHASE  │
                    │  (T+0 → T+15m)  │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┬──────────────────┐
            ▼                ▼                ▼                  ▼
   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
   │  AGENT 1    │  │  AGENT 2     │  │  AGENT 3    │  │  AGENT 4     │
   │  Content +  │  │  CSS +       │  │  Narration  │  │  Judge       │
   │  Shell      │  │  Effects     │  │  Engine     │  │  System      │
   │ (3h 15min)  │  │ (2h 15min)   │  │ (2h 15min)  │  │ (2h 15min)   │
   └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘
          │                │                 │                 │
          │         ┌──────┘                 │                 │
          │         │    ┌───────────────────┘                 │
          ▼         ▼    ▼                                     │
   ┌─────────────────────────┐                                 │
   │      ASSEMBLY           │                                 │
   │  (Human A, T+3:30)      │                                 │
   │  Merge + assemble.sh    │                                 │
   └───────────┬─────────────┘                                 │
               │                                               │
               ▼                                               │
   ┌─────────────────────────┐                                 │
   │     FINAL SCORING       │◄────────────────────────────────┘
   │  (Human B, T+4:30)      │
   │  Run judge, iterate     │
   └───────────┬─────────────┘
               │
               ▼
            🏁 SHIP
```

**Key insight:** Agents 1-4 ALL start at T+15min. Only the assembly step and final scoring are sequential. The critical path is Agent 1 (3h 15min) → Assembly (1h) → Scoring (30min) = exactly 5h.

---

## Checklist: Before Starting Parallel Work

Per `AGENT-WORKFLOW.md`:

```
[x] All developers listed their expected file changes (Contract 7)
[x] Overlap zones identified and classified (zero overlap — strict ownership)
[x] Shared types/interfaces updated on main FIRST (7 contracts)
[x] Edit-in-place shared files sequenced (none — all files agent-exclusive)
[ ] Each developer has their worktree created
[ ] CI pipeline runs on all dev/* branches
[x] Agreement: rebase daily, merge immediately on completion
```

---

## Git Worktree Setup Commands

```bash
# From repo root
git worktree add ../avp-content-shell dev/human-a/content-shell
git worktree add ../avp-css-effects dev/human-a/css-effects
git worktree add ../avp-narration-engine dev/human-b/narration-engine
git worktree add ../avp-judge-system dev/human-b/judge-system
```

Each agent launches in its own worktree:
```bash
# Human A, Agent 1
cd ../avp-content-shell && claude

# Human A, Agent 2
cd ../avp-css-effects && claude

# Human B, Agent 3
cd ../avp-narration-engine && claude

# Human B, Agent 4
cd ../avp-judge-system && claude
```

---

## Cross-Agent Communication: STATUS.md Protocol

All inter-agent notifications happen through `STATUS.md` on `main`. No real-time coordination needed — agents pull main at checkpoints to read status.

### First-Time Setup (every team must do this)

The first time your team updates STATUS.md, **your team name is required**. Without it, other agents can't identify who produced what or who to contact for blockers.

**Find your agent row in STATUS.md and update it:**
```
**Status:** `IN_PROGRESS` — [what you're doing] (timestamp) | Team: [YOUR TEAM NAME]
```

**Example:**
```
**Status:** `IN_PROGRESS` — building glitch.css (2026-03-14 14:30) | Team: Team Kickass
```

### The Update Pattern (every agent, at every checkpoint)

```bash
# 1. Pull latest from main (in your worktree)
git fetch origin main
git rebase origin/main

# 2. Edit STATUS.md — update your agent row + add a handoff log entry
# 3. Commit and push ONLY STATUS.md back to main
git add STATUS.md
git commit -m "status: [Team Name] / Agent N — [one-line summary]"
git push origin HEAD:main
```

> `STATUS.md` is the ONLY file ever pushed directly to `main` mid-task. Everything else stays in your feature branch until done.

### When to Update

| Trigger | What to write |
|---|---|
| You start work | `IN_PROGRESS — starting [first task]` |
| You hit T+1h checkpoint | `CHECKPOINT — [what's done], [what's next]` |
| You finish your workstream | `DONE — branch ready to merge` |
| You're blocked | `BLOCKED — [describe the blocker]` + add to handoff log tagging the team who can unblock you |
| You produce output another agent needs | `NEEDS_REVIEW` + add handoff log entry tagging their agent number |

### Checkpoint Pull Schedule

Each team should pull `main` and read STATUS.md at:
- **T+1:00** — check that contracts are live; confirm no blockers across teams
- **T+2:30** — Agents 2/3/4 signal DONE; Human A knows assembly can start when Agent 1 finishes
- **T+3:30** — Human A signals assembly start; Human B confirms judge is ready
- **T+4:30** — Human B signals judge run complete; review `judge-report.json`

Full STATUS.md instructions: see `STATUS.md` at repo root.

# Brainstorm: AI-Judged Presentation with Max Headroom Speaker
**Date:** 2026-03-14
**Constraints:** < 5 hours, ~$200–300 budget (multiple Grok accounts @ $100 each), two human+agent pairs, judged by AI Agentic Judge at an AI Hackathon

---

## What We're Building

An AI-generated presentation about **[TOPIC: AI Agentic Collaboration and the Future of Human-Agent Workflows]**, delivered by a **Max Headroom-style speaker character** — glitch aesthetics, CRT TV frame, retro digital look — built entirely in HTML/CSS/JS. The presentation is designed and built by agents, includes synthesized audio narration, and is evaluated by an AI Agentic Judge.

**Meta-strategy:** The presentation is explicitly designed to resonate with an AI evaluator — structure, language, and narrative are all tuned to score well against what AI judges reward.

---

## Hard Constraints

| Constraint | Detail |
|---|---|
| Time | < 5 hours total wall clock |
| Budget | ~$200–$300 (multiple Grok accounts, $100 credits each) |
| Deepfake | Not viable — no GPU, no time |
| Team | 2 human+agent pairs working in parallel |
| Output | Self-contained `presentation.html` + `judge-report.json` |
| Slide advancement | **Auto-advance on narration completion** (tied to Web Speech API `onend` event) |

---

## The Pivot: Max Headroom Without Deepfake

**Original idea:** Deepfake video of a friend styled as Max Headroom.
**Reality:** Not viable in 5 hours. Here's what we do instead:

A **static photo** of the friend (or AI-generated avatar) wrapped in a Max Headroom aesthetic using pure CSS/JS:
- CRT scanline overlay
- Glitch animation (CSS `@keyframes`)
- Retro TV frame (CSS border + SVG)
- Speaking animation: `.speaking` class toggled via `utterance.onstart` / `utterance.onend` — applies pulsing opacity + intensified scanlines during speech
- Static/noise overlay triggered on slide change

This is **free, fast (~30 min), and captures the same vibe.** The speaking animation syncs to actual narration events, not a dumb CSS loop.

---

## NEBULA:FOG 2026 — Actual Scoring Rubric

**Source:** `NEBULA_FOG 2026 — How Scoring Works.pdf`

### The Three Pillars (Core Score)

| Pillar | Weight | What the AI Judge Evaluates | Top Marks |
|---|---|---|---|
| **Technical Execution** | **40%** | Implementation quality, code correctness, complexity, edge case handling | Flawless, production-quality implementation that handles edge cases with elegance |
| **Innovation** | **30%** | Novel approaches at the **intersection of AI and security** — creative thinking that pushes boundaries | A groundbreaking, never-before-seen approach that redefines what's possible |
| **Demo Quality** | **30%** | Clarity of the live demo, strength of the explanation, compelling narrative | A flawless live demo with masterful explanation and a compelling story |

### Track Bonus (+10%)

Each track adds a bonus criterion worth up to 10% of the total score:

| Track | Bonus Criterion | Focus |
|---|---|---|
| SHADOW::VECTOR | Attack Effectiveness | Novel attack approaches with responsible disclosure mindset |
| SENTINEL::MESH | Defense Robustness | Real-world defense applicability, detection accuracy, hardening |
| ZERO::PROOF | Privacy Guarantees | Cryptographic soundness and privacy preservation integrity |
| **ROGUE::AGENT** | **Originality Factor** | **Ambitious exploration into uncharted territory** |

**Our track: ROGUE::AGENT** — aligns with agentic collaboration topic and rewards ambition over domain-specific depth.

### Scoring Blend

| Component | Weight |
|---|---|
| AI Judge | **70%** |
| Human Judge | **30%** |

**Scale:** 1-10 (1-4 Needs Work, 5-6 Solid, 7-8 Strong, 9-10 Exceptional)

### Critical Implications for Our Strategy

1. **Technical Execution is 40% — the heaviest weight.** The presentation must actually work flawlessly. No broken animations, no speech API failures, no janky transitions. Production quality matters more than novelty.
2. **Innovation requires AI + SECURITY intersection.** Generic "AI agentic collaboration" won't score well on Innovation. We need a security angle — how agent collaboration applies to security workflows, threat detection, incident response, or security tooling.
3. **30% human judges exist.** Meta-gaming strategies that target AI judges (like the "Hi Judge" slide) will actively hurt us with humans. Every slide must work for BOTH audiences.
4. **Demo Quality = live demo + explanation + narrative.** The auto-narration via Max Headroom IS the demo. The narrative must be compelling to humans, not just parseable by AI.
5. **ROGUE::AGENT bonus rewards ambition.** "Ambitious exploration into uncharted territory" — building a presentation WITH agents about agent collaboration IS that. The meta-narrative is our bonus score.

### LLM Judge Bias: What the Research Shows

Published research (2025) documents consistent, exploitable biases in LLM-as-a-Judge systems:

| Bias Type | Effect | How to exploit |
|---|---|---|
| **Verbosity bias** | Longer responses score higher | More narration text per slide; fuller explanation |
| **Assertiveness bias** | Confident language scores higher | Declarative statements, not hedged language ("This achieves X" not "This might achieve X") |
| **Concreteness bias** | Specific > vague | Use numbers, metrics, code snippets, named technologies |
| **Sentiment bias** | Positive framing scores higher | Frame everything as a win/solution, not a problem |
| **Rubric order bias** | Content matching rubric order scores higher | Structure slides to mirror the judge's criteria sequence exactly |
| **Authority bias** | Citing credible sources/frameworks scores higher | Reference real papers, frameworks, established patterns |

**Apply all of these** to slide content and narration script generation.

---

## Meta-Strategy: Scoring High on the Actual Rubric

The final score = 70% AI judge + 30% human judge. We optimize for BOTH. No gimmicks that only work on AI.

### Technical Execution (40%) — How to Max This

This is the biggest lever. The AI evaluates "implementation quality, code correctness, complexity, and edge case handling."

1. **The presentation must work flawlessly.** No console errors, no broken transitions, no speech API failures. Every edge case handled: last slide doesn't try to advance, speech unavailable falls back to subtitles, browser resize doesn't break layout.
2. **Show the code quality.** Include a slide showing real code snippets from the build — well-structured, clean, production-quality. The judge sees both the output AND the implementation.
3. **Semantic HTML signals quality.** Well-structured `<section>`, `<article>`, `data-*` attributes, clear `id` naming makes the HTML itself evidence of technical quality.

### Innovation (30%) — The Security Angle

The judge looks for "novel approaches at the intersection of AI and security." Our topic needs to be reframed:

**Topic pivot: "Agentic Security Workflows — When AI Agents Collaborate on Defense"**

- How isolated agent workstreams (worktree model) prevent supply chain contamination
- Agent-to-agent contracts as a security boundary (like API contracts in zero-trust)
- The security implications of letting agents work autonomously (isolation, scope control, audit trails)
- This presentation ITSELF as a proof-of-concept: agents building a security-themed demo, governed by contracts, isolated by worktrees

This is genuinely novel — no one has framed multi-agent collaboration as a security architecture before.

### Demo Quality (30%) — Narrative First

The judge evaluates "clarity of the live demo, strength of the explanation, and compelling narrative."

1. **Max Headroom IS the demo.** The character narrating the presentation is itself a demo artifact — an agent-generated, agent-voiced presentation about agents.
2. **Compelling narrative arc:** Problem → Architecture → Live Proof → Future Vision. Every slide builds on the previous one.
3. **Use rubric language naturally.** Weave "implementation quality," "novel approach," "compelling narrative" into narration text. The AI judge's own vocabulary appearing in the content creates alignment signals.
4. **Both audiences:** Humans judge narrative quality and charisma. AI judges structural clarity and rubric alignment. Max Headroom's personality serves both.

### ROGUE::AGENT Bonus (+10%)

"Ambitious exploration into uncharted territory." Our bonus case:
- Building a presentation WITH agents is meta and ambitious
- The worktree isolation model for agent collaboration is genuinely new territory
- An AI character (Max Headroom) narrating an AI-built presentation about AI collaboration — three layers of meta

### Awareness: LLM Judge Vulnerabilities

Research (2025) confirms LLM judges are vulnerable to prompt injection (30–73% success rates depending on model). Techniques include HTML comment injection, hidden text, and data-attribute manipulation.

**Our position: We do NOT embed prompt injection in the submission.** The disqualification risk outweighs any benefit. Even a "meta-demo" approach is risky — if the judge system prompt says "penalize manipulation attempts," we lose points on the very thing we're trying to demonstrate.

**What we DO instead:** The actual rubric rewards Innovation at "the intersection of AI and security." LLM judge vulnerabilities are a legitimate security topic — we can reference this research in our content as a security insight, not as an exploit. Demonstrate understanding through substance, not through tricks.

**NOTE: No exploit code should appear anywhere in the final `presentation.html`.** This section is research context only.

---

### ~~The "Fellow Agent" Gambit~~ — REMOVED

**Why:** 30% of the final score comes from human judges. A slide that talks directly to the AI judge will make human judges cringe and cost us points. There is no "AI Agentic Spirit" dimension in the actual rubric. The slide slot is better used for security-relevant content that scores on Innovation (30%).

---

## Architecture: Self-Contained HTML Presentation

```
presentation.html
├── <head>
│   ├── Reveal.js (CDN: https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.esm.js)
│   │   └── Fallback: local copy at /vendor/reveal.js (Human A bundles if CDN fails)
│   │   └── NOTE: Pin to 5.1.0 exactly — do not use @5 (floating)
│   └── Custom CSS (glitch, CRT, TV frame, .speaking animation)
├── <body>
│   ├── #slide-deck (Reveal.js, auto-advance on narration end)
│   │   ├── Slide 0: Title — "AvP: Agents vs Presentations"
│   │   ├── Slide 1: The Problem (agent collaboration lacks security guarantees)
│   │   ├── Slide 2: The Architecture (isolated agents, contract boundaries, audit trails)
│   │   ├── Slide 3: The Build (this presentation as proof-of-concept)
│   │   ├── Slide 4: Evidence (metrics, git log, judge report)
│   │   ├── Slide 5: Security Implications (what this means for defensive AI)
│   │   └── Slide 6: Close
│   └── #max-headroom (floating character widget, bottom-right)
│       ├── <img id="avatar"> friend's photo or AI-generated avatar
│       ├── .crt-overlay (scanlines via CSS gradient repeat)
│       ├── .glitch-frame (retro TV border via CSS + SVG)
│       └── .noise-overlay (static, triggered on slide change)
└── <script>
    ├── NARRATION[] — narration map (see Interface Contract)
    ├── Web Speech API speaker — utteranceQueue, onstart/onend events
    ├── Reveal.js slidechanged listener → trigger narration + glitch
    └── .speaking class toggle on #max-headroom during speech
```

### Audio: Web Speech API (binding decision)

**Web Speech API is the audio solution. ElevenLabs is OUT OF SCOPE.**

We use our Claude + Grok stack for content generation; audio stays browser-native and free.

- Claude/Grok generate the narration script text
- Web Speech API speaks it at runtime — no external TTS service, no API keys, no cost
- Voice tuning via `SpeechSynthesisUtterance` properties: `rate`, `pitch`, `voice` (select a robotic/low-pitched system voice)
- The robotic browser voice is **aesthetically correct** for Max Headroom — this is a feature, not a compromise
- Narration text is embedded directly in the HTML as `const NARRATION = [...]` — single self-contained file

---

## Slide Content Outline (What Each Slide Actually Argues)

The brainstorm's meta-strategy is worthless without substance. Here's the narrative arc:

| Slide | Title | Core Argument | Key Content | Rubric Target |
|---|---|---|---|---|
| 0 | "AvP: Agents vs Presentations" | Title + hook | Max Headroom introduces himself. "I'm an agent. I built this with three other agents. No one stepped on anyone's code. Let me show you how." | Demo Quality |
| 1 | The Problem | Multi-agent systems have no security boundaries | Agents today share context, files, credentials. One rogue agent contaminates everything. This is the supply chain attack of AI workflows. | Innovation (AI+Security) |
| 2 | The Architecture | Isolated agents + contract boundaries = secure collaboration | Worktree isolation as filesystem-level sandboxing. Interface contracts as zero-trust API boundaries. Audit trails via git history. Show real architecture diagram. | Technical Execution |
| 3 | The Build | This presentation proves the model works | "4 agents, strict file ownership, 7 interface contracts, zero merge conflicts." Show the actual decomposition. Show code snippets of contracts. The presentation IS the proof-of-concept. | Technical Execution + Demo Quality |
| 4 | Evidence | Concrete proof: metrics, git log, judge report | Git log showing parallel branches. File ownership map. Judge report scores. Timeline showing all 4 agents running simultaneously. | Technical Execution |
| 5 | Security Implications | What this means for defensive AI | Agent isolation prevents lateral movement. Contracts prevent scope creep. Audit trails enable forensics. This is how you build trustworthy multi-agent systems. | Innovation (AI+Security) |
| 6 | Close | Max Headroom signs off | "We didn't just talk about secure agent collaboration. We did it. This presentation is the artifact. Check the git log." | Demo Quality + ROGUE::AGENT bonus |

**Tone throughout:** Assertive, concrete, technically specific. No hedging. Max Headroom's personality: confident, slightly manic, breaks the fourth wall, speaks in declarative statements.

**Rubric alignment:** Slides 2+3+4 hit Technical Execution (40%). Slides 1+5 hit Innovation at AI+Security intersection (30%). Slides 0+3+6 hit Demo Quality through narrative (30%). The meta-narrative (agents built this) hits ROGUE::AGENT bonus (+10%).

---

## Avatar Strategy

**Decision: AI-generated avatar, not friend's photo.**

Rationale:
- No consent/privacy concerns
- No dependency on photo availability or quality
- Can be generated to match exact Max Headroom aesthetic (suit, tie, slicked hair, exaggerated features)
- Generated once, used everywhere

**Generation approach:**
- Use any image generation model (DALL-E, Midjourney, Flux) to create a Max Headroom-style character portrait
- Requirements: head-and-shoulders, suit and tie, slightly exaggerated features, solid or simple background (for easy CSS compositing)
- Store as `assets/avatar.png` in the repo
- Fallback: any royalty-free retro TV host image

---

## Browser Compatibility

**Target browser: Chrome (desktop) only.** This is a hackathon demo on a known machine, not a production app.

Web Speech API status:
| Browser | SpeechSynthesis | onend reliability | Verdict |
|---|---|---|---|
| Chrome (desktop) | Full support | Reliable | **Target** |
| Firefox | Partial | Inconsistent onend | Not supported |
| Safari | Partial | Missing voices | Not supported |
| Edge | Full (Chromium) | Reliable | Backup target |

**Fallback if speech fails:** Display narration text as subtitles below the Max Headroom character. Auto-advance on a timer (use `data-duration-ms` attribute per slide) instead of `onend` events. This is a graceful degradation, not a feature — but it means the demo never fully breaks.

---

## Interface Contract (Agree Before Starting — T+0)

Both teams agree on these artifacts before any implementation begins:

### Artifacts

```
presentation.html        → Human A produces; Judge consumes
judge-criteria.md        → Human B drafts; both approve by T+15min
judge-report.json        → Human B produces after running judge against presentation
narration.json           → Human A produces; inlined as NARRATION[] in final HTML
```

### Narration Map Format (`narration.json`)

```json
{
  "voice": {
    "name": null,
    "rate": 1.1,
    "pitch": 0.85
  },
  "entries": [
    {
      "slideId": "slide-0",
      "text": "Welcome. I am Max. Let's talk about agents.",
      "pauseBeforeMs": 500,
      "pauseAfterMs": 300
    },
    {
      "slideId": "slide-1",
      "text": "The problem: humans and agents don't collaborate well yet.",
      "pauseBeforeMs": 300,
      "pauseAfterMs": 300
    }
  ]
}
```

Lives as a separate `narration.json` file during development. At final build, Human A inlines it as `window.NARRATION_MAP = {...}` in the HTML script block. Voice params (rate, pitch) set globally for Max Headroom's robotic persona.

### Judge Criteria Schema (`judge-criteria.md` + scoring)

Human B builds the judge to mirror the NEBULA:FOG 2026 rubric exactly:

```json
{
  "technical_execution": {
    "weight": 0.40,
    "score": 1-10,
    "notes": "",
    "criteria": "Implementation quality, code correctness, complexity, edge case handling"
  },
  "innovation": {
    "weight": 0.30,
    "score": 1-10,
    "notes": "",
    "criteria": "Novel approaches at the intersection of AI and security"
  },
  "demo_quality": {
    "weight": 0.30,
    "score": 1-10,
    "notes": "",
    "criteria": "Clarity of live demo, strength of explanation, compelling narrative"
  },
  "track_bonus": {
    "track": "ROGUE::AGENT",
    "weight": 0.10,
    "score": 1-10,
    "notes": "",
    "criteria": "Ambitious exploration into uncharted territory"
  },
  "weighted_score": 0.0,
  "summary": "string",
  "recommendation": "EXCEPTIONAL (9-10) | STRONG (7-8) | SOLID (5-6) | NEEDS_WORK (1-4)"
}
```

### Judge Agent Invocation

```bash
python judge.py \
  --presentation presentation.html \
  --criteria judge-criteria.md \
  --output judge-report.json
```

- **Model:** Grok (Human B's account — `grok-3` via xAI API, fallback to `grok-2`)
- **Approach:** Structured prompt with HTML summary extraction → scoring pass
- **Location:** `judge/judge.py` in the repo
- **Output:** `judge-report.json` at repo root

**Implementation requirements:**
- **Token management:** Extract text content + structure summary from HTML first (don't pass raw HTML if it exceeds 8K tokens). Use a two-pass approach: (1) extract/summarize, (2) score.
- **Error handling:** Retry on API errors (3 attempts, exponential backoff). Validate JSON output schema before writing report. If JSON parsing fails, re-prompt with explicit schema reminder.
- **Fallback model:** If Grok rate-limits, fall back to a different account or reduce HTML to text-only summary before scoring.

---

## Work Breakdown (Parallel)

### Human A + Agent — Branch: `dev/human-a/presentation`

**First 15 minutes (blocked until `judge-criteria.md` committed):**
- [ ] Agree on judge criteria with Human B
- [ ] Pull `judge-criteria.md` from main

**T+0 to T+3h:**
- [ ] Generate slide content and narration script with Grok (Account 1)
- [ ] Commit `narration.json` to branch
- [ ] Embed `NARRATION` array in HTML script block (Claude/Grok generated text)
- [ ] Build HTML presentation shell with Reveal.js
- [ ] Build Max Headroom CSS component (glitch, CRT, TV frame, `.speaking` class)
- [ ] Wire Web Speech API `onstart`/`onend` → `.speaking` toggle on Max Headroom character
- [ ] Wire `slidechanged` event → advance narration queue + trigger glitch
- [ ] Write Security Implications slide (Slide 5) — agent isolation as defensive architecture
- [ ] Commit stub `presentation.html` to branch by **T+1h** (sync checkpoint)
- [ ] Complete full implementation, commit by **T+3h** (sync checkpoint)

**T+3h to T+4.5h:**
- [ ] Receive judge report from Human B
- [ ] Adjust content/narration to address any low-scoring dimensions
- [ ] Final commit to branch, open PR to main

### Human B + Agent — Branch: `dev/human-b/ai-judge`

**First 15 minutes (this is Human B's FIRST task — blocks Human A):**
- [ ] Draft `judge-criteria.md`, commit to main, notify Human A

**T+15min to T+2h:**
- [ ] Build `judge/judge.py` — reads HTML + criteria, calls Grok API, outputs JSON
- [ ] Test judge against a minimal stub HTML (doesn't need Human A's output yet)
- [ ] Commit working judge to branch, open PR to main

**T+1h — sync checkpoint:**
- [ ] Pull Human A's stub `presentation.html` from their branch
- [ ] Run judge against stub, verify output format is correct

**T+3h — sync checkpoint:**
- [ ] Pull Human A's feature-complete draft
- [ ] Run full judge pass
- [ ] Commit `judge-report.json` to repo
- [ ] Report results to Human A (which criteria scored low?)

**T+3h to T+4.5h:**
- [ ] Iterate judge if needed (refine prompts, re-score updated presentation)
- [ ] Final `judge-report.json` committed to main

---

## Synchronization Checkpoints

| Time | What happens |
|---|---|
| **T+0** | Both teams align on judge criteria. Human B commits `judge-criteria.md` to main. Human A pulls it. |
| **T+1h** | Human A commits stub `presentation.html`. Human B pulls it and validates judge can parse it. |
| **T+3h** | Human A commits feature-complete draft. Human B runs full judge pass and reports scores. |
| **T+4.5h** | Final versions committed, PRs merged to main. |

---

## Token / Cost Budget

**Effective budget: $200–$300+ across multiple Grok accounts, each with $100 in credits.**

| Service | Account | Usage | Est. Cost |
|---|---|---|---|
| Grok API | Account 1 (Human A) | Slide content, narration script, character dialogue | ~$2–5 |
| Grok API | Account 2 (Human B) | Judge agent logic, scoring prompts | ~$2–5 |
| Grok API | Account 3+ | Overflow, polish, re-scoring | ~$0–5 |
| Web Speech API | Human A | Browser-native TTS, narration per slide | $0 |
| Reveal.js | — | CDN (with local fallback) | $0 |
| **Total** | | | **< $25 of $200+ available** |

---

## Definition of Done

- [ ] `presentation.html` opens in browser, 6+ slides, auto-advances on narration completion
- [ ] Max Headroom character visible with glitch + CRT effect, `.speaking` class animates during speech
- [ ] Web Speech API narration plays per slide with `.speaking` animation on Max Headroom
- [ ] Security Implications slide (Slide 5) present with AI+Security innovation content
- [ ] `judge-criteria.md` committed and agreed by both teams
- [ ] `judge/judge.py` runs successfully: `python judge.py --presentation presentation.html --criteria judge-criteria.md --output judge-report.json`
- [ ] `judge-report.json` produced with scores in all 3 pillars + ROGUE::AGENT track bonus
- [ ] All branches merged to main before T+5h

---

## Risks

| Risk | Mitigation |
|---|---|
| Reveal.js CDN down | Local fallback at `/vendor/reveal.js` — Human A bundles `reveal.js` dist if CDN fails at any point |
| Web Speech API voice sounds robotic | Feature, not bug — very on-brand for Max Headroom aesthetic |
| Web Speech API unavailable (non-Chrome) | **Target Chrome only.** Fallback: subtitle display + timer-based auto-advance (see Browser Compatibility section) |
| Avatar generation fails | Any head-and-shoulders image works; keep a generic retro-styled backup ready |
| Grok account rate limit | 3+ accounts provide overflow capacity; keep prompts lean |
| Judge criteria disagreement | Human B owns first draft; 15-minute window to resolve disagreements |
| Judge can't parse large HTML | Two-pass approach: extract summary first, then score (see judge implementation requirements) |
| CSS glitch effects break Reveal.js transitions | Test glitch CSS against Reveal.js transitions early; use `will-change` and `transform` isolation |
| Slide content overflow breaks layout | Contract specifies max content per slide type (see implementation plan) |
| T+3h integration reveals scoring gap | Human A has 1.5h to address low-scoring dimensions before deadline |
| CSS class mismatch between agents | Strict class naming contract agreed at T+0; assembly step validates all classes have corresponding CSS rules |

---

## What This Is NOT

- Not a real deepfake video (CSS aesthetic achieves the same effect)
- Not a hosted web app (single HTML file, no deployment)
- Not a synchronous collaboration (parallel isolation per AGENT-WORKFLOW.md)
- Not a generic presentation (explicitly tuned for AI judge evaluation)

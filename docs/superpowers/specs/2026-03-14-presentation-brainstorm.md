# Brainstorm: AI-Judged Presentation with Max Headroom Speaker
**Date:** 2026-03-14
**Constraints:** < 5 hours, ~$0 budget, two human+agent pairs, judged by AI Agentic Judge

---

## What We're Building

An AI-generated presentation delivered by a **Max Headroom-style speaker character** — glitch aesthetics, CRT TV frame, retro digital look — built entirely in HTML/CSS/JS. The presentation itself is designed and built by agents, includes synthesized audio narration, and is evaluated by an AI Agentic Judge.

---

## Hard Constraints

| Constraint | Detail |
|---|---|
| Time | < 5 hours total wall clock |
| Budget | ~$0 (free tiers only) |
| Deepfake | Not viable — no GPU, no time, no money |
| Team | 2 human+agent pairs working in parallel |
| Output | Must be judgeable by an AI Agentic Judge |

---

## The Pivot: Max Headroom Without Deepfake

**Original idea:** Deepfake video of a friend styled as Max Headroom.
**Reality:** Deepfake requires GPU, time, and $$$. Not viable in 5 hours at $0.

**What we do instead:**
A **static photo** of the friend (or AI-generated avatar) wrapped in a Max Headroom aesthetic using pure CSS/JS:
- CRT scanline overlay
- Glitch animation (CSS `@keyframes`)
- Retro TV frame (CSS border + SVG)
- "Speaking" lip-sync illusion via animated opacity on the photo
- Static/noise overlay on trigger

This is **free, fast (~30 min), and captures the same vibe.**

---

## Approaches Considered

### Option A: Self-Contained HTML Presentation (Recommended)
**Single HTML file** with embedded CSS, JS, audio, and the Max Headroom component.
- Reveal.js or custom slide system
- Web Speech API for TTS (free, browser-native) OR pre-baked MP3 from ElevenLabs free tier
- Max Headroom character embedded as a floating component on slides
- AI Judge receives the HTML file and evaluates it

**Why recommended:** Zero dependencies, instantly shareable, works offline, trivially judgeable by an AI agent (just read the HTML).

### Option B: Hosted Web App
Next.js or similar, deployed to Vercel free tier. More impressive but adds deployment complexity and risk.
**Rejected:** Adds 1-2 hours of setup risk. Not worth it in a 5-hour window.

### Option C: Slide Deck (PDF/PPTX)
Generated programmatically. Simple but no audio, no animation, no Max Headroom character.
**Rejected:** Loses the most interesting parts of the vision.

---

## Architecture: Option A (Self-Contained HTML)

```
presentation.html
├── <head>
│   ├── Reveal.js (CDN)
│   └── Custom CSS (glitch, CRT, TV frame)
├── <body>
│   ├── #slide-deck (Reveal.js slides)
│   │   ├── Slide 1: Title
│   │   ├── Slide 2–N: Content slides
│   │   └── Slide N+1: Closing
│   └── #max-headroom (floating character widget)
│       ├── <img> friend's photo (or AI avatar)
│       ├── .crt-overlay (scanlines)
│       ├── .glitch-frame (TV border)
│       └── .noise-overlay (static)
└── <script>
    ├── Slide narration map (slide index → text)
    ├── Web Speech API speaker (utteranceQueue)
    └── Glitch trigger on slide change
```

### Audio Strategy
- **Primary:** Web Speech API — zero cost, built into every browser, no API key
- **Fallback:** ElevenLabs free tier (10k chars/month) for a pre-rendered MP3 per slide if richer voice is needed
- Narration script is agent-generated from slide content

### AI Judge Integration
The judge receives:
1. The `presentation.html` file (readable as text)
2. A `judge-criteria.md` file defining scoring rubric
3. The judge returns a structured score (JSON or markdown)

---

## Work Breakdown (Parallel, Per AGENT-WORKFLOW.md)

### Human A + Agent (Presentation & Max Headroom)
Branch: `dev/human-a/presentation`

- [ ] Define slide content and narration script (agent generates)
- [ ] Build HTML presentation shell (Reveal.js + custom CSS)
- [ ] Build Max Headroom CSS component (glitch, CRT, TV frame)
- [ ] Wire Web Speech API narration to slide transitions
- [ ] Add friend's photo (or placeholder avatar)
- [ ] Test end-to-end in browser

**Estimated time:** 3–4 hours

### Human B + Agent (AI Judge)
Branch: `dev/human-b/ai-judge`

- [ ] Define judge criteria (`judge-criteria.md`)
- [ ] Build judge agent script (reads HTML, scores against criteria)
- [ ] Use Grok free tier or any available API for judge LLM call
- [ ] Output structured score report (`judge-report.md` or JSON)
- [ ] Test against a draft of the presentation HTML

**Estimated time:** 2–3 hours

---

## Interface Contract (Agree Before Starting)

Both teams must agree on this before parallel work begins:

```
presentation.html     → the deliverable, Human A produces, Judge consumes
judge-criteria.md     → the rubric, Human B produces, both teams agree on it FIRST
judge-report.json     → the judge output, Human B produces
```

**Criteria fields (draft — agree before work starts):**
```json
{
  "clarity": 0-10,
  "creativity": 0-10,
  "technical_execution": 0-10,
  "entertainment_value": 0-10,
  "ai_agentic_spirit": 0-10,
  "total": 0-50,
  "summary": "string"
}
```

---

## Token / Cost Budget

**Effective budget: $200–$300+ across multiple Grok accounts, each with $100 in credits.**

| Service | Usage | Cost |
|---|---|---|
| Grok API (Account 1 — Human A) | Slide content, narration script, character dialogue | ~$0–5 |
| Grok API (Account 2 — Human B) | Judge agent logic, scoring, iteration | ~$0–5 |
| Grok API (Account 3+ — overflow) | Re-generation, polish passes | ~$0–5 |
| ElevenLabs | High-quality voice synthesis (paid tier unlocked by budget) | ~$5–10 |
| Web Speech API | Fallback / quick iteration | $0 |
| Reveal.js | Presentation framework | $0 (CDN) |
| **Total** | | **< $20 of $200+ available** |

**Token split strategy:** Each account is dedicated to a role so we never hit rate limits mid-task:
- **Account 1 (Human A):** All presentation content generation
- **Account 2 (Human B):** All judge agent and scoring logic
- **Account 3+:** Overflow, iteration, polish, and re-scoring

With $100/account we have headroom for rich prompts, multiple generation passes, and ElevenLabs professional voice without worrying about cost.

---

## Definition of Done

- [ ] `presentation.html` opens in browser, slides advance, Max Headroom character visible with glitch effect
- [ ] Audio narration plays (Web Speech API or ElevenLabs MP3)
- [ ] `judge-criteria.md` committed and agreed
- [ ] `judge-report.json` produced by the AI Judge agent after reading the presentation
- [ ] Both branches merged to main before the 5-hour mark

---

## Risks

| Risk | Mitigation |
|---|---|
| Web Speech API voice sounds robotic | Acceptable — very on-brand for a Max Headroom theme |
| Friend's photo not available | Use an AI-generated avatar as placeholder |
| Grok free tier runs out | Split across two accounts; keep prompts short |
| Reveal.js CDN unavailable | Bundle locally or use a minimal custom slider |
| Judge criteria disagreement | Agree on `judge-criteria.md` in the first 15 minutes |

---

## What This Is NOT

- Not a real deepfake video
- Not a hosted web app (no deployment needed)
- Not reliant on paid APIs
- Not a synchronous collaboration (agents work in parallel isolation per AGENT-WORKFLOW.md)

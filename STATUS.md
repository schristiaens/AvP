# Agent Status Board

Cross-agent notifications via git. Update your row and commit to `main` at each checkpoint.
Each team pulls `main` to read status before/after sync points.

**Format:** `[STATUS] short note (timestamp)`
**Statuses:** `BLOCKED` | `IN_PROGRESS` | `CHECKPOINT` | `DONE` | `NEEDS_REVIEW`

---

## Sync Checkpoints

| Time | Event |
|---|---|
| T+0:00 | Contracts agreed, all agents unblock |
| T+1:00 | Agent 2 stub commit; all agents check in |
| T+2:30 | Agents 2, 3, 4 done — notify Human A |
| T+3:30 | Agent 1 done — Human A begins assembly |
| T+4:30 | Assembly validated — Human B runs judge |
| T+5:00 | 🏁 SHIP |

---

## Agent 1 — Content + Shell (Human A)
> Branch: `dev/human-a/content-shell` | Files: `content/`, `src/shell.html`, `src/slides/`, `build/`

**Status:** `WAITING` — pending contract commit on main (T+0)

---

## Agent 2 — CSS + Visual Effects (Human A / Team Kickass)
> Branch: `dev/human-a/css-effects` | Files: `src/styles/`, `assets/`

**Status:** `IN_PROGRESS` — worktree created, starting theme.css (2026-03-14)

---

## Agent 3 — Narration Engine (Human B)
> Branch: `dev/human-b/narration-engine` | Files: `src/js/`

**Status:** `WAITING` — pending contract commit on main (T+0)

---

## Agent 4 — Judge System (Human B)
> Branch: `dev/human-b/judge-system` | Files: `judge/`

**Status:** `WAITING` — pending contract commit on main (T+0)

---

## Handoff Log

| Time | From | To | Message |
|---|---|---|---|
| 2026-03-14 | Human A | All | Worktree for Agent 2 created. Team Kickass is live on `dev/human-a/css-effects`. |

---

## How to Update Your Status (Read This First)

### Step 1 — Pull latest main into your worktree
```bash
git fetch origin main
git rebase origin/main
```

### Step 2 — Edit STATUS.md

Update **two things:**

**a) Your agent row** — replace the status line with:
```
**Status:** `IN_PROGRESS` — [what you're doing] (YYYY-MM-DD HH:MM) | Team: [YOUR TEAM NAME]
```

**b) Add a row to the Handoff Log:**
```
| 2026-03-14 HH:MM | [Your Team Name] / Agent N | [Target: Agent N or "All"] | [Message] |
```

> **Team name is required on every update.** Without it, other agents don't know who to contact if there's a blocker.

### Step 3 — Commit and push to main
```bash
git add STATUS.md
git commit -m "status: [Team Name] / Agent N — [one-line summary]"
git push origin HEAD:main
```

> **IMPORTANT:** Only `STATUS.md` is ever committed directly to `main` mid-task. All other work stays in your feature branch until your agent is done.

### Status Values

| Status | Meaning |
|---|---|
| `WAITING` | Blocked on contract agreement or another agent |
| `IN_PROGRESS` | Actively building |
| `CHECKPOINT` | Hit a sync point — check handoff log for details |
| `NEEDS_REVIEW` | Produced output, needs another team to look at it |
| `DONE` | Branch complete, ready to merge |
| `BLOCKED` | Stuck — describe the blocker in the handoff log |

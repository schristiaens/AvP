# Multi-Developer Agent Workflow Plan

## The Core Principle

Coordination happens **before** work (contracts) and **after** work (integration). The work itself is fully isolated — no real-time coordination needed.

---

## Layer 1: Isolation — Worktree Per Work Item

Each developer-agent pair gets their own filesystem via git worktrees:

```bash
# Alice starts her work item
claude --worktree auth-refactor

# Bob starts his
claude --worktree payment-flow

# Carol starts hers
claude --worktree api-endpoints
```

**Branch naming:** `dev/{person}/{slug}`

```
main (protected, CI-gated)
  ├── dev/alice/auth-refactor
  ├── dev/bob/payment-flow
  └── dev/carol/api-endpoints
```

**Rules:**
- One worktree per work item (a developer can have multiple)
- Never work directly on main
- Each worktree = completely isolated filesystem, no cross-contamination

---

## Layer 2: Coordination — Contracts Before Work

Before anyone starts parallel work, do a 10-minute decomposition:

1. **Each developer lists their expected file changes** — even rough guesses help
2. **Identify overlap zones** — files touched by 2+ developers
3. **For each overlap, classify and decide:**

| File Type | Strategy | Examples |
|---|---|---|
| **Generated** | Don't commit from branches; regenerate on main | `package-lock.json`, build output |
| **Append-only** | Safe to parallelize — git auto-merges these | Adding exports to `index.ts`, adding config entries |
| **Type definitions / interfaces** | Change FIRST on main before parallel work starts | Shared types, API schemas, `.d.ts` files |
| **Edit-in-place configs** | Sequence: one person edits, merges, others rebase | `tsconfig.json`, CI configs |

4. **Define interface contracts** for anything that crosses boundaries — function signatures, API shapes, shared types. Agree on these before starting. Put them in code (types, interfaces) on main so everyone branches from the same contracts.

---

## Layer 3: Integration — Rebase Daily, Merge Immediately on Completion

**Two rhythms:**

### Daily rebase (every developer, in their worktree):
```bash
git fetch origin main
git rebase origin/main
# Agent resolves most conflicts automatically
# Flag anything non-trivial to the developer
```

### Merge on completion (don't batch, don't wait):
```bash
# Work item done → PR immediately
gh pr create --base main --title "dev/alice/auth-refactor"
# CI runs, quick review, merge
# Everyone else rebases to pick up the changes
```

**The critical rule:** First to finish merges first. Everyone else rebases. Don't accumulate branches — the longer they live, the harder they merge.

---

## Layer 4: Failure Modes & Recovery

| What Goes Wrong | How You Detect It | How You Fix It |
|---|---|---|
| Textual merge conflict | `git rebase` fails | Agent resolves most automatically; human reviews complex ones |
| Semantic conflict (compiles, but broken) | CI tests fail after merge | Revert merge, fix in branch, re-merge |
| Contract violation (interface changed) | TypeScript/compiler error | Contract changer updates all callers before merging |
| Stale branch (too far behind) | Massive rebase conflicts | New worktree from fresh main, re-apply changes |
| Two agents edited same file | Rebase conflict | First to merge wins, second rebases |
| Agent goes off-rails | Developer monitoring | Kill agent, `git stash`, restart with clearer prompt |

---

## Practical Checklist — Before Starting Parallel Work

```
[ ] All developers listed their expected file changes
[ ] Overlap zones identified and classified
[ ] Shared types/interfaces updated on main FIRST
[ ] Edit-in-place shared files sequenced (who goes first)
[ ] Each developer has their worktree created
[ ] CI pipeline runs on all dev/* branches
[ ] Agreement: rebase daily, merge immediately on completion
```

---

## Scaling Notes

- **2-3 developers:** Verbal decomposition is fine. Slack thread listing file ownership works.
- **4-6 developers:** Write the file ownership map down. Consider a shared doc or issue with the decomposition.
- **7+ developers:** You need an integration lead whose job is to sequence merges and resolve cross-cutting conflicts. The overhead is worth it.
- **Same developer, multiple agents:** Same rules apply — each agent gets its own worktree. The developer is their own integration lead.

---

## For AI Agents Reading This

If you are a Claude Code agent working in this repo:

1. **You are in a worktree.** Your branch is isolated. Work freely within your scope.
2. **Don't touch files outside your work item's scope** unless your developer explicitly asks.
3. **Rebase from main when your developer tells you to**, or proactively suggest it if you notice your branch is behind.
4. **If you hit a merge conflict**, resolve it if straightforward. If it involves semantic changes you're unsure about, flag it to your developer.
5. **Respect interface contracts.** If shared types or interfaces exist, use them as-is. Don't change them without your developer's explicit approval.
6. **When done**, help your developer create a PR with a clear description of what changed and why.

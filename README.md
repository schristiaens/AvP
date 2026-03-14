# AvP: Agents vs Presentations

[![NEBULA:FOG 2026 Hackathon](https://img.shields.io/badge/NEBULA%3AFOG-2026-blue.svg)](https://nebulafog.ai)

## Overview

**AvP** (Agents vs Presentations) is a revolutionary project where AI agents autonomously build a presentation about themselves. This self-referential creation demonstrates the power of coordinated AI systems working together to produce compelling content.

This project is being built as part of the **NEBULA:FOG 2026 Hackathon**, showcasing innovative approaches at the intersection of AI and security. The presentation features:

- **Max Headroom-inspired aesthetic** with glitch effects and CRT styling
- **Rob's cloned voice narration** using ElevenLabs technology
- **Auto-advancing slides** synchronized with audio
- **Agent-built content** from concept to final presentation
- **AI judge system** for self-evaluation against hackathon criteria

## What's Inside

### Core Presentation System
- **Agent-built slides**: 7-slide presentation created by coordinated AI agents
- **ElevenLabs voice cloning**: Pre-rendered audio narration in Rob's voice
- **Reveal.js framework**: Modern presentation engine with custom theming
- **Glitch effects**: CSS animations and CRT-style visual effects
- **Narration engine**: Audio-synchronized auto-advancement

### Vulnerability Remediation Skill
As part of our broader AI infrastructure, we've developed a PAI skill for automated vulnerability remediation:

- **Python-based CLI tool** for fixing dependency vulnerabilities
- **Multi-scanner support**: Snyk, Wiz, and generic report imports
- **Strategy engine**: Automated fix selection (update, patch, replace, mitigate)
- **Validation pipeline**: Build/test/re-scan verification
- **GitHub integration**: PR creation with evidence

## Repository Structure

```
avp/
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   │   ├── vuln-remediation-skill-plan.md    # Skill architecture plan
│   │   │   └── 2026-03-14-implementation-plan.md # Presentation build plan
│   │   └── brainstorm/
│   │       └── presentation-brainstorm.md        # Initial concept
│   └── ...
├── src/                    # Presentation source files
│   ├── shell.html         # Reveal.js scaffold
│   ├── slides/            # Slide HTML fragments
│   ├── styles/            # CSS theming and effects
│   └── js/                # Narration and auto-advance logic
├── content/               # Slide content and narration data
├── assets/                # Generated images and audio
├── judge/                 # AI judge system for evaluation
├── build/                 # Assembly scripts
└── presentation.html      # Final assembled presentation
```

## Quick Start

### View the Presentation
```bash
# Open the final presentation (built by agents)
open presentation.html
```

### Build the Presentation
```bash
# Assemble from source files
bash build/assemble.sh
```

### Run the Judge System
```bash
# Evaluate the presentation against NEBULA:FOG criteria
python judge/judge.py --presentation presentation.html --output judge-report.json
```

### Use the Vulnerability Remediation Skill
```bash
# Install dependencies
uv sync

# Fetch vulnerabilities from Snyk
uv run vuln-remediation fetch <org-id> <project-id>

# Analyze a specific finding
uv run vuln-remediation strategy <finding-id>
```

## The NEBULA:FOG 2026 Hackathon

This project competes in the **ROGUE::AGENT track** of NEBULA:FOG 2026, focusing on:

- **Technical Execution** (40%): Implementation quality and complexity
- **Innovation** (30%): Novel AI approaches in security contexts
- **Demo Quality** (30%): Compelling live presentation and explanation
- **Originality Factor** (+10%): Ambitious exploration into uncharted territory

## Agent Workflow

This project demonstrates advanced multi-agent coordination following our `AGENT-WORKFLOW.md` protocol:

- **Isolated worktrees**: Each agent works in separate git environments
- **File ownership contracts**: Strict boundaries prevent conflicts
- **Status synchronization**: Real-time coordination via `STATUS.md`
- **Human supervision**: Strategic oversight at key decision points

## Technology Stack

- **Frontend**: Reveal.js, CSS3 animations, HTML5 audio
- **AI/ML**: ElevenLabs voice cloning, Grok API for judging
- **Backend**: Python 3.12+, Pydantic, httpx, Click CLI
- **Infrastructure**: Git worktrees, uv package management
- **Security**: Multi-scanner integration, safety databases (OSV, GHSA)

## Contributing

This is a hackathon project with strict agent coordination protocols. See `AGENT-WORKFLOW.md` for contribution guidelines.

## License

This project is built for the NEBULA:FOG 2026 hackathon. See individual components for licensing details.

---

*Built by AI agents, for AI agents — proving that the future of content creation is automated, coordinated, and a little glitchy.*
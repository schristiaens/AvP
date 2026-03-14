# AvP: Agents vs Presentations

[![NEBULA:FOG 2026 Hackathon](https://img.shields.io/badge/NEBULA%3AFOG-2026-blue.svg)](https://nebulafog.ai)

## Overview

**AvP** is a dual-component project built for the **NEBULA:FOG 2026 Hackathon**, combining cutting-edge AI automation with practical security tooling. The project consists of two equally important pillars:

## 🖥️ Component 1: The Presentation Layer

A revolutionary self-referential presentation where **AI agents autonomously build a presentation about themselves**. This demonstrates coordinated AI systems producing compelling content from concept to delivery.

**Key Features:**
- **Max Headroom-inspired aesthetic** with glitch effects and CRT styling
- **Rob's cloned voice narration** using ElevenLabs technology
- **Auto-advancing slides** synchronized with audio
- **Agent-built content** from concept to final presentation
- **AI judge system** for self-evaluation against hackathon criteria

**Technology Stack:**
- Reveal.js presentation framework
- ElevenLabs voice cloning and audio generation
- CSS3 animations and visual effects
- Git-based multi-agent coordination

## 🔧 Component 2: Automated Vulnerability Patching Skill

A comprehensive **PAI skill for automated vulnerability remediation** in software dependencies. This Python-based CLI tool enables security engineers to fix vulnerabilities with minimal manual intervention.

**Key Features:**
- **Multi-scanner support**: Snyk, Wiz, and generic report imports
- **Intelligent strategy engine**: Automated fix selection (update, patch, replace, mitigate)
- **Validation pipeline**: Build/test/re-scan verification before PR creation
- **Safety checks**: OSV and GHSA database integration
- **GitHub integration**: Automated PR creation with evidence

**Technology Stack:**
- Python 3.12+ with uv package management
- Pydantic for data validation
- httpx for async HTTP operations
- Click CLI framework
- Jinja2 templating

## Both Components Are Equally Important

While the presentation serves as our **hackathon showcase**, the vulnerability remediation skill represents **practical AI tooling** that can be deployed in production environments. Together, they demonstrate the full spectrum of AI capabilities: from creative content generation to mission-critical security automation.

## What's Inside

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
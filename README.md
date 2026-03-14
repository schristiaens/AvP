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

## 🛠️ Using the Vulnerability Remediation Skill

The vulnerability remediation skill is a standalone CLI tool that helps security engineers identify and fix dependency vulnerabilities.

### Prerequisites

Before using the skill, ensure you have:

- **Python 3.12+** installed
- **uv** package manager: `pip install uv` or `brew install uv`
- **GitHub CLI** (`gh`) authenticated: `gh auth login`
- **Scanner API tokens** (optional, for enhanced functionality):
  - Snyk token: `SNYK_TOKEN` environment variable
  - Wiz token: `WIZ_TOKEN` environment variable

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/schristiaens/AvP.git
   cd AvP/skills/VulnRemediation
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Verify installation:**
   ```bash
   uv run vuln-remediation --help
   ```

### Configuration

Create environment variables for API access (optional but recommended):

```bash
# Snyk API token (for vulnerability scanning)
export SNYK_TOKEN="your-snyk-api-token"

# GitHub CLI authentication (for PR operations)
gh auth login

# Optional: Wiz token for additional scanning
export WIZ_TOKEN="your-wiz-api-token"
```

### Usage Examples

#### 1. Fetch Vulnerabilities from Snyk
```bash
# Fetch all high/critical vulnerabilities from a Snyk project
uv run vuln-remediation fetch your-org your-project-id

# Filter by ecosystem (npm, maven, docker)
uv run vuln-remediation fetch your-org your-project-id --ecosystem npm

# Get JSON output for scripting
uv run vuln-remediation fetch your-org your-project-id --output json
```

#### 2. Check Package Safety Against Databases
```bash
# Check if a specific version has known vulnerabilities
uv run vuln-remediation osv-check pkg:npm/lodash 4.17.20

# This queries OSV.dev and returns:
# {
#   "version": "4.17.20",
#   "safe": false,
#   "advisories": ["GHSA-29mw-wpgm-hmr9", "GHSA-35jh-r3h4-6jhm"],
#   "severity_introduced": null
# }
```

#### 3. Analyze Breaking Changes Between Versions
```bash
# Check what changed between versions
uv run vuln-remediation changelog lodash 4.17.19 4.17.20

# Returns breaking change analysis:
# {
#   "semver_delta": "patch",
#   "changelog_url": "https://www.npmjs.com/package/lodash/v/4.17.20",
#   "breaking_changes": [],
#   "deprecations": [],
#   "api_changes": []
# }
```

#### 4. Check for Existing Remediation Work
```bash
# Search for existing PRs/branches for an advisory
uv run vuln-remediation dedup-check your-org/your-repo GHSA-29mw-wpgm-hmr9

# Returns:
# {
#   "existing_pr": null,
#   "existing_branch": null
# }
```

#### 5. Render PR Templates
```bash
# Create sample remediation data
cat > sample-data.json << 'EOF'
{
  "findings": [{
    "finding_id": "test-finding",
    "package_name": "lodash",
    "current_version": "4.17.19",
    "severity": "high",
    "advisory_ids": ["GHSA-29mw-wpgm-hmr9"]
  }],
  "strategy": {
    "recommended_strategy": "update",
    "target_version": "4.17.21",
    "confidence": 0.9,
    "rationale": "Safe patch update available"
  },
  "validation": {
    "success": true,
    "build_passed": true,
    "test_passed": true,
    "rescan_clean": true
  }
}
EOF

# Render PR body
uv run vuln-remediation render-pr sample-data.json

# Render reviewer checklist
uv run vuln-remediation render-checklist sample-data.json

# Render decision log
uv run vuln-remediation render-decision-log sample-data.json
```

### Workflow Integration

The skill is designed to be used as part of a larger remediation workflow:

1. **Discover**: Use `fetch` to identify vulnerabilities
2. **Assess**: Use `osv-check` and `changelog` to evaluate fix options
3. **Plan**: Use `dedup-check` to avoid duplicate work
4. **Execute**: Apply fixes and validate with build/test
5. **Document**: Use `render-*` commands to create PR content

### Getting Help

```bash
# See all available commands
uv run vuln-remediation --help

# Get help for specific commands
uv run vuln-remediation fetch --help
uv run vuln-remediation osv-check --help
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
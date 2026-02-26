<div align="center">

# NagaAgent

**Your Ultimate AI Secretary**

Streaming Tool Calls · Knowledge Graph Memory · Live2D Avatar · Voice Interaction · Naga Network Community

[简体中文](README.md) | [English](README_en.md)

![NagaAgent](https://img.shields.io/badge/NagaAgent-5.1.0-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-AGPL%203.0%20%7C%20Proprietary-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)

[![Stars](https://img.shields.io/github/stars/Xxiii8322766509/NagaAgent?style=social)](https://github.com/Xxiii8322766509/NagaAgent)
[![Forks](https://img.shields.io/github/forks/Xxiii8322766509/NagaAgent?style=social)](https://github.com/Xxiii8322766509/NagaAgent)
[![Issues](https://img.shields.io/github/issues/Xxiii8322766509/NagaAgent)](https://github.com/Xxiii8322766509/NagaAgent/issues)

**[QQ Bot Integration: Undefined QQbot](https://github.com/69gg/Undefined/)**

</div>

---

**Dual Licensed** · Open source under [AGPL-3.0](LICENSE) · Closed-source under [Proprietary License](LICENSE-CLOSED-SOURCE) (written consent required).
Commercial inquiries: contact@nagaagent.com / bilibili [柏斯阔落]

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 🎆 2026-02-26 | 5.1.0 | Naga Network community forum launched; unified settings page (3-in-1 redesign); travel mode; credits quota page; market & panel updates |
| ⚡ 2026-02-25 | 5.1.0 | TTS full-stack fix (CORS / asyncio); cross-platform build.py; context compression persistence; character system update; prompt injection refactor |
| 🎵 2026-02-24 | — | Neo4j connection timeout fix; unified BGM player; MusicBox playlist editor; MCP management UI; floating ball transparent window + hover brightness |
| 🏗️ 2026-02-23 | — | Cross-platform build improvements; version unified in pyproject.toml; prompt/screenshot/visual optimization; character file migration & packaging |
| 💕 2026-02-22 | — | Credits & affinity system (check-in / affinity / credits); floating ball shadow & drag fix; auto login restore; OpenClaw hooks fix |
| 🎶 2026-02-21 | — | MusicBox icon update; MCP Agents update; floating ball mini-buttons |
| 🗜️ 2026-02-20 | — | 3-tier context compression refactor (`<compress>` tag / cross-session inheritance); MCP management UI; floating ball transparent window; MusicBox fixes |
| 🔄 2026-02-19 | — | SSE removes base64, direct JSON streaming; remove redundant background intent analyzer; config_manager auto-detect encoding |
| 🔧 2026-02-17 | — | Floating ball sprite frame path changed to relative, fixes missing avatar in packaged build |
| 🚀 2026-02-16 | 5.0.0 | NagaModel gateway unified access; DeepSeek reasoning chain real-time display; Mind Sea UI adaptive fix |
| 🧠 2026-02-15 | — | Unified knowledge block injection + history pollution fix; LLM streaming retry; 7-day auto-login; auto-start on boot |
| 🌊 2026-02-14 | — | NagaMemory cloud remote memory; Mind Sea 3D rewrite; splash particle animation; version update dialog; user agreement |
| ✨ 2026-02-13 | — | Floating ball 4-state mode; screenshot multimodal vision switch; skill workshop refactor; Live2D emotion channel independent |
| 🎨 2026-02-12 | — | NagaCAS authentication; Live2D 4-channel orthogonal animation; Agentic Tool Loop; Arknights-style splash screen |
| 📦 2026-02-11 | — | Embedded OpenClaw packaging; auto-generate config from template on startup |
| 🛠️ 2026-02-10 | — | Backend packaging optimization; skill workshop MCP status fix; remove redundant Agent/MCP keeping only OpenClaw |
| 🌱 2026-02-09 | — | Frontend refactor; Live2D eye tracking disabled; OpenClaw renamed to AgentServer |

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Feature Overview (Main Panel)](#feature-overview-main-panel)
3. [Chat](#1-chat--messageview)
4. [Mind Sea](#2-mind-sea--mindview)
5. [Skill Workshop](#3-skill-workshop--skillview)
6. [Naga Network](#4-naga-network--community-forum)
7. [Ark Market](#5-ark-market--marketview)
8. [Terminal Settings](#6-terminal-settings--configview)
9. [MusicBox](#7-musicbox--musicview)
10. [Floating Ball](#8-floating-ball--floatingview)
11. [Global Features](#global-features)
12. [Backend Architecture](#backend-architecture)
13. [Optional Configuration](#optional-configuration)
14. [Ports](#ports)
15. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Requirements

- Python 3.11 (`>=3.11, <3.12`)
- Optional: [uv](https://github.com/astral-sh/uv) — faster dependency installation
- Optional: Neo4j — local knowledge graph memory

### Installation

```bash
git clone https://github.com/Xxiii8322766509/NagaAgent.git
cd NagaAgent

# Frontend
cd frontend
npm install
cd ..

# Backend
# Option 1: Setup script (auto-detects env, creates venv, installs deps)
python setup.py

# Option 2: uv
uv sync

# Option 3: Manual
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### Minimal Configuration

Copy `config.json.example` to `config.json` and fill in your LLM API credentials:

```json
{
  "api": {
    "api_key": "your-api-key",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-v3.2"
  }
}
```

Works with any OpenAI-compatible API (DeepSeek, Qwen, OpenAI, Ollama, etc.).

### Launch

```bash
cd frontend && npm run dev   # one-click launch (configured)
```

---

## Feature Overview (Main Panel)

After launch, you enter the **Main Panel (PanelView)** with a 3D parallax effect (perspective rotation driven by mouse movement).
All features are accessible through eight entry buttons on the main panel:

| # | Entry | Route | Summary |
|---|-------|-------|---------|
| 1 | **Chat** | `/chat` | AI conversation, streaming tool calls, context compression |
| 2 | **Mind Sea** | `/mind` | Knowledge graph 3D visualization & GRAG memory management |
| 3 | **Skill Workshop** | `/skill` | MCP tool management & community Skill installation |
| 4 | **Naga Network** | `/forum` / `/forum/quota` | Community forum, credits & affinity |
| 5 | **Ark Market** | `/market` | Backgrounds, music, characters, memory migration, recharge |
| 6 | **Terminal Settings** | `/config` | Model, memory & audio/visual config (3-in-1) |
| 7 | **MusicBox** | `/music` | BGM player & playlist management |
| 8 | **Floating Ball** | — | Enter lightweight floating ball window mode |

---

## 1. Chat · MessageView

### Streaming Tool Calls

The chat engine streams output via SSE, simultaneously sending to the frontend display and TTS sentence splitting.
Tool calls do not rely on OpenAI's Function Calling API — the LLM embeds JSON inside ` ```tool``` ` code blocks, so **any OpenAI-compatible provider works out of the box**.

**Single-round tool call flow:**

```
LLM streaming output ──SSE──▶ Frontend real-time display
       │
       ▼
parse_tool_calls_from_text()
  ├─ Phase 1: Extract ```tool``` code blocks
  └─ Phase 2: Fallback to bare JSON extraction
       │
       ▼
  Route by agentType
  ├─ "mcp"      → MCPManager.unified_call()
  ├─ "openclaw" → Agent Server /openclaw/send
  └─ "live2d"   → UI animation notification
       │
       ▼
  asyncio.gather() parallel execution of all tools
       │
       ▼
  Inject results into messages, start next LLM round (up to 5)
```

- Text parsing: `json5` tolerant parsing, fullwidth characters auto-normalized
- SSE format: `data: {"type":"content"|"reasoning","text":"..."}\n\n` (direct JSON, no base64)
- Loop limit: `max_loop_stream = 5` (configurable)

Source: [`apiserver/agentic_tool_loop.py`](apiserver/agentic_tool_loop.py)

### Context Compression

Automatically triggered when session tokens exceed 100k, preventing context overflow:

| Phase | Trigger | Behavior |
|-------|---------|---------|
| **Startup Compression** | Session load | Immediately compress early messages if history exceeds threshold |
| **Runtime Compression** | After each round | Compress and inject `<compress>` tag when over limit |
| **Cross-session Inheritance** | New session start | Read previous summary, roll up accumulated context |

Summary structure (6 sections): Key facts / User preferences / Important decisions / To-dos / Background info / Recent state.
The `<compress>` tag persists to the session file but is not counted in LLM token statistics.

### DeepSeek Reasoning Chain Display

When using DeepSeek, the `reasoning` field is pushed in real-time via SSE and displayed in a distinct style in the frontend.

---

## 2. Mind Sea · MindView

### GRAG Knowledge Graph Memory

GRAG (Graph-RAG) automatically extracts quintuples from conversations, stores them in Neo4j, and retrieves relevant memories as LLM context.

**Quintuple structure:** `(subject, subject_type, predicate, object, object_type)`

**Extraction pipeline:**

1. Structured extraction (preferred): `beta.chat.completions.parse()` + Pydantic `QuintupleResponse`, `temperature=0.3`, up to 3 retries
2. JSON fallback: on parse failure, extract content from the first `[` to the last `]`
3. Filtering: keep only facts (behaviors, relations, states, preferences); filter metaphors, hypotheticals, emotions

**Entity types:** `person` / `location` / `organization` / `item` / `concept` / `time` / `event` / `activity`

**Task manager:**
- 3 asyncio workers consuming `asyncio.Queue(maxsize=100)`
- SHA-256 deduplication: identical pending/running tasks are skipped
- Hourly cleanup of tasks older than 24h

**Dual storage:**
- Local: `logs/knowledge_graph/quintuples.json`
- Cloud: Neo4j graph database, `graph.merge()` upsert

**RAG retrieval:** Keyword extraction → Cypher query → formatted as `subject(type) —[predicate]→ object(type)` injected into context

**Remote memory:** Logged-in users automatically use NagaMemory cloud; falls back to local GRAG on logout or offline.

Source: [`summer_memory/`](summer_memory/)

### Mind Sea 3D Visualization

Canvas 2D + hand-rolled 3D projection (not WebGL), spherical coordinate camera, perspective division `700 / depth`.

**7-layer render order:**
Background gradient → floor grid → water surface → volumetric light (3 god rays) → particle system (3 layers, 125 particles) → bioluminescent plankton (10 with trails) → knowledge graph nodes & edges (depth-sorted)

**Graph mapping:** `subject/object` → nodes, `predicate` → directed edges, degree centrality → node height weight, 100-node limit

**Interactions:** Drag to orbit, middle-click to pan, scroll to zoom, node click/drag, keyword search filter

---

## 3. Skill Workshop · SkillView

### Built-in MCP Agents

A pluggable tool architecture based on the [Model Context Protocol](https://modelcontextprotocol.io/), each tool running as an independent Agent:

| Agent | Function |
|-------|----------|
| `weather_time` | Weather query / forecast, system time, auto city / IP detection |
| `open_launcher` | Scan installed apps, launch programs via natural language |
| `game_guide` | Game strategy Q&A, damage calc, team building, auto-screenshot injection |
| `online_search` | Web search via SearXNG |
| `crawl4ai` | Web content extraction via Crawl4AI |
| `playwright_master` | Browser automation via Playwright |
| `vision` | Screenshot analysis & visual Q&A |
| `mqtt_tool` | IoT device control via MQTT |
| `office_doc` | docx / xlsx content extraction |

**Registration & discovery:** `mcp_registry.py` glob-scans `**/agent-manifest.json`, dynamically instantiates via `importlib.import_module`.

### MCP Management UI

The frontend `McpAddDialog.vue` provides a graphical MCP tool management interface — add or remove tools at runtime without restarting.

### Community Skill Installation

The Skill Workshop supports one-click installation of community-published Skills (Agent Browser, Brainstorming, Context7, Firecrawl Search, etc.).
Backend endpoints: `GET /openclaw/market/items`, `POST /openclaw/market/items/{id}/install`

Source: [`mcpserver/`](mcpserver/)

---

## 4. Naga Network · Community Forum

### Community Forum

Accessible from the "Naga Network" block on the main panel, with a fully embedded community:

| View | Route | Function |
|------|-------|----------|
| `ForumListView` | `/forum` | Post list, category filter |
| `ForumPostView` | `/forum/post/:id` | Post details & replies |
| `ForumMessagesView` | `/forum/messages` | Direct messages |
| `ForumMyPostsView` | `/forum/my-posts` | My posts |
| `ForumMyRepliesView` | `/forum/my-replies` | My replies |
| `ForumQuotaView` | `/forum/quota` | Credits quota & explore entry |

Source: [`frontend/src/forum/`](frontend/src/forum/)

### Credits & Affinity System

A gamified interaction system exclusive to logged-in users:

| Dimension | Description |
|-----------|-------------|
| **Credits** | Earned through daily check-in and streak bonuses; used to redeem model quota |
| **Affinity** | Increases with each check-in; reflects relationship depth with Naga |
| **Daily Check-in** | One-click check-in from user menu; consecutive check-ins trigger bonus rewards |

Related APIs (proxied through API Server to the Naga portal): `/api/checkin`, `/api/affinity`, `/api/credits`

---

## 5. Ark Market · MarketView

The Ark Market consolidates all resource acquisition and management, organized into seven tabs:

| Tab | Description |
|-----|-------------|
| **Theme Background** | Switch application background theme |
| **Music Alley** | Purchase / unlock music albums (current: Book of Sand) |
| **Character Registration** | Bind / switch AI character (login required) |
| **Memory Migration** | Cloud memory data migration & management |
| **MCP Tools** | MCP tool graphical management |
| **Agent Skills** | Community Skill one-click installation |
| **Model Recharge** | Naga portal credit top-up |

---

## 6. Terminal Settings · ConfigView

Settings page redesigned as a single page with three tabs (3-in-1 unification):

| Tab | Contents |
|-----|---------|
| **Model Connection** | LLM API Key, Base URL, model selection |
| **Memory Connection** | Neo4j connection params, NagaMemory cloud config |
| **Audio/Visual Config** | Character profile, Live2D model & SSAA, TTS voice, chat font size |

### Character Card System

The `characters/` directory manages switchable AI characters, each described by a JSON config file:

```json
{
  "ai_name": "Najezhda",
  "user_name": "User",
  "live2d_model": "NagaTest2/NagaTest2.model3.json",
  "prompt_file": "conversation_style_prompt.txt",
  "portrait": "Naga.png",
  "bio": "An AI assistant created by developer 柏斯阔落, nicknamed Naga."
}
```

- Each character directory contains an independent conversation style prompt, Live2D model assets, and portrait image
- Once a character is activated, AI name and Live2D model are managed entirely by the character JSON and cannot be manually overridden in the UI
- Default character: **Najezhda**

Source: [`characters/`](characters/)

---

## 7. MusicBox · MusicView

A standalone music player that **shares the same playback instance** as the main interface BGM (unified BGM architecture):

- **Playlist Editor** (`MusicEditView`): Manage track list; changes sync to the global player immediately on save
- **Playback state sync**: Play / pause icon updates in real time with audio events
- **Loop**: Automatically advances to the next track when the current one ends
- **Live2D lip sync**: During TTS playback, `AdvancedLipSyncEngineV2` drives Live2D mouth shapes at 60FPS

---

## 8. Floating Ball · FloatingView

Click the "Float" button on the main panel to enter the lightweight floating ball window, cycling through four states:

```
ball (100×100 circle) → compact (420×100 collapsed bar) → full (420×N expanded) → classic (normal window)
```

**Appearance & animation:**
- Sprite-frame blink animation: 5 frames (open → half-closed → closed → half-closed → open), 70ms/frame, random interval trigger
- While generating a reply: glowing halo pulse effect
- On hover: brightness lift effect
- Transparent frameless window, freely draggable

**Features:**
- Chat input available directly in floating state; message history viewable in compact / full states
- Screenshot capture panel: select a screen window as an image attachment
- File upload support
- Right-click menu implemented via Electron native menu (prevents clipping in small window)

---

## Global Features

### Voice Interaction

**TTS (Text-to-Speech)**

- Engine: Edge-TTS, OpenAI-compatible endpoint `/v1/audio/speech`
- Architecture: 3-thread pipeline — sentence queue → TTS calls (Semaphore(2) concurrency) → pygame playback
- Live2D lip sync: 60FPS extraction of 5 parameters (mouth_open / mouth_form / mouth_smile / eye_brow_up / eye_wide)
- Port cleanup: auto-detects and releases occupied ports at startup

**ASR (Speech Recognition)**

- Local engine: FunASR, with VAD endpoint detection and WebSocket real-time streaming
- Three-mode auto-switch: `LOCAL` (FunASR) → `END_TO_END` (Qwen Omni) → `HYBRID`

**Realtime Voice Chat** (requires DashScope API Key)

- Full-duplex WebSocket voice interaction via Qwen Omni
- Echo suppression, VAD detection, audio chunking (200ms), session cooldown control

```json
{
  "voice_realtime": {
    "enabled": true,
    "provider": "qwen",
    "api_key": "your-dashscope-key",
    "model": "qwen3-omni-flash-realtime"
  }
}
```

Source: [`voice/`](voice/)

---

### Live2D Avatar

Renders Cubism Live2D models using **pixi-live2d-display** + **PixiJS WebGL**.
SSAA super-sampling: Canvas rendered at `width × ssaa`, CSS `transform: scale(1/ssaa)`.

**4-channel orthogonal animation system** (`live2dController.ts`):

| Channel | Controls | Features |
|---------|----------|---------|
| **Body State** | idle / thinking / talking loop | Hermite smooth interpolation, loaded from `naga-actions.json` |
| **Action** | Nod / shake head and other head actions | FIFO queue, single execution |
| **Emotion** | `.exp3.json` expression files | Add / Multiply / Overwrite blend modes, exponential decay transition |
| **Tracking** | Mouse gaze following | Configurable start delay via `tracking_hold_delay_ms` |

Merge order: body state → mouth → action → manual override → emotion blend → tracking blend

---

### OpenClaw Computer Control

Interfaces with the OpenClaw Gateway (port 18789) to dispatch AI coding assistants for local tasks via natural language.

- **3-tier fallback startup:** packaged binary → global `openclaw` command → auto `npm install -g openclaw`
- Supports sessionKey hooks (2026.2.17+), configurable custom hooks path
- `POST /openclaw/send` sends instructions, waits up to 120 seconds

**Task Scheduler (`TaskScheduler`):**
- Task step recording (purpose / content / output / analysis / success status)
- Auto-extraction of "key findings" markers
- Memory compression: when steps exceed threshold, LLM generates `CompressedMemory` (key_findings / failed_attempts / current_status / next_steps)
- `schedule_parallel_execution()` runs task lists in parallel via `asyncio.gather()`

Source: [`agentserver/`](agentserver/)

---

### Splash Animation

| Phase | Content |
|-------|---------|
| **Title phase** | Black overlay + 40 golden rising particles + title image 2.4s CSS keyframe; wake voice plays when title appears |
| **Progress phase** | Neural network particle background + Live2D cutout frame + gold progress bar (`requestAnimationFrame` interpolation, minimum speed 0.5 floor) |
| **Stall detection** | Restart hint shown after 3s with no progress; backend `/health` polled every second after 25% |
| **Awaken** | Pulsing "Click to Awaken" prompt appears when progress reaches 100% |

---

## Backend Architecture

NagaAgent consists of four independent microservices, all orchestrated by `main.py`:

```
┌─────────────────────────────────────────────────────────┐
│                   Electron / PyQt5 Frontend              │
│  Vue 3 + Vite + UnoCSS + PrimeVue + pixi-live2d-display │
│                                                         │
│  PanelView · MessageView · MindView · SkillView         │
│  MarketView · ConfigView · MusicView · FloatingView     │
│  ForumListView · ForumPostView · ForumQuotaView …       │
└──────────┬─────────────┬──────────────┬─────────────────┘
           │             │              │
   ┌───────▼──────┐ ┌────▼────┐  ┌─────▼──────┐
   │  API Server  │ │  Agent  │  │   Voice    │
   │   :8000      │ │  Server │  │  Service   │
   │              │ │  :8001  │  │   :5048    │
   │ Chat / SSE   │ │         │  │            │
   │ Tool calls   │ │ Task    │  │ TTS / ASR  │
   │ Compression  │ │ schedule│  │ Realtime   │
   │ Doc upload   │ │ OpenClaw│  │ voice      │
   │ Auth proxy   │ │         │  │            │
   │ Memory API   │ └────┬────┘  └────────────┘
   │ Skill Market │      │
   │ Config mgmt  │  ┌───▼──────────┐
   └──────┬───────┘  │  OpenClaw    │
          │          │  Gateway     │
   ┌──────▼──────┐   │  :18789      │
   │ MCP Server  │   └─────────────┘
   │   :8003     │
   │ Tool registry│
   │ Agent disco │
   │ Parallel    │
   └──────┬──────┘
          │
  ┌───────┴───────────────────────┐
  │      MCP Agents (pluggable)   │
  │ Weather | Search | Crawl      │
  │ Launcher | Guide | Doc | MQTT │
  └───────────────────────────────┘
          │
   ┌──────▼──────┐
   │    Neo4j    │
   │   :7687     │
   │  Knowledge  │
   │   Graph     │
   └─────────────┘
```

### Directory Structure

```
NagaAgent/
├── main.py                   # Unified entry point, orchestrates all services
├── build.py                  # Cross-platform build script
├── config.json               # Runtime config (copied from config.json.example)
├── pyproject.toml            # Version 5.1.0, project metadata & dependencies
│
├── apiserver/                # API Server (:8000)
│   ├── api_server.py         #   FastAPI main app
│   ├── agentic_tool_loop.py  #   Multi-round tool call loop
│   ├── llm_service.py        #   LiteLLM unified LLM interface
│   └── streaming_tool_extractor.py  # Streaming sentence split + TTS dispatch
│
├── agentserver/              # Agent Server (:8001)
│   ├── agent_server.py
│   └── task_scheduler.py     #   Task orchestration + compressed memory
│
├── mcpserver/                # MCP Server (:8003)
│   ├── mcp_server.py
│   ├── mcp_registry.py       #   Manifest scanning + dynamic registration
│   ├── mcp_manager.py        #   unified_call() routing
│   ├── agent_weather_time/
│   ├── agent_open_launcher/
│   ├── agent_game_guide/
│   ├── agent_online_search/
│   ├── agent_crawl4ai/
│   ├── agent_playwright_master/
│   ├── agent_vision/
│   ├── agent_mqtt_tool/
│   └── agent_office_doc/
│
├── summer_memory/            # GRAG knowledge graph memory
│   ├── quintuple_extractor.py
│   ├── quintuple_graph.py
│   ├── quintuple_rag_query.py
│   ├── task_manager.py
│   ├── memory_manager.py
│   └── memory_client.py      #   NagaMemory remote client
│
├── voice/                    # Voice service (:5048)
│   ├── output/               #   TTS + lip sync
│   └── input/                #   ASR + realtime voice
│
├── characters/               # Character config directory
│   └── Najezhda/             #   prompt / Live2D model / portrait
│
├── frontend/                 # Electron + Vue 3 frontend
│   ├── electron/             #   Main process
│   │   └── modules/          #   backend / hotkeys / menu / tray / updater / window
│   └── src/
│       ├── views/            #   All page views
│       ├── forum/            #   Forum module
│       ├── components/       #   Shared components
│       ├── composables/      #   useAuth / useBackground / useAudio …
│       └── utils/            #   live2dController / session / config
│
├── system/                   # Config loader, env checker, system prompts
├── guide_engine/             # Game guide engine
└── logs/                     # Runtime logs, knowledge graph files
```

---

## Optional Configuration

<details>
<summary><b>Knowledge Graph Memory (Neo4j)</b></summary>

Install Neo4j ([Docker](https://hub.docker.com/_/neo4j) or [Neo4j Desktop](https://neo4j.com/download/)), then configure `config.json`:

```json
{
  "grag": {
    "enabled": true,
    "neo4j_uri": "neo4j://127.0.0.1:7687",
    "neo4j_user": "neo4j",
    "neo4j_password": "your-password"
  }
}
```

Without Neo4j, GRAG uses local JSON file storage only — functionality is not affected.
</details>

<details>
<summary><b>Voice Interaction (TTS / ASR)</b></summary>

```json
{
  "system": { "voice_enabled": true },
  "tts": {
    "port": 5048,
    "default_voice": "zh-CN-XiaoxiaoNeural"
  }
}
```

Full-duplex realtime voice chat (requires Qwen DashScope API Key):

```json
{
  "voice_realtime": {
    "enabled": true,
    "provider": "qwen",
    "api_key": "your-dashscope-key",
    "model": "qwen3-omni-flash-realtime"
  }
}
```
</details>

<details>
<summary><b>Live2D Avatar (Custom Model)</b></summary>

```json
{
  "web_live2d": {
    "ssaa": 2,
    "model": {
      "source": "./models/your-model/model.model3.json",
      "x": 0.5,
      "y": 1.3,
      "size": 6800
    },
    "face_y_ratio": 0.13,
    "tracking_hold_delay_ms": 100
  }
}
```

When a character card is active, `ai_name` and `model.source` are automatically overridden by the character JSON — no manual edits needed.
</details>

<details>
<summary><b>MQTT IoT Control</b></summary>

```json
{
  "mqtt": {
    "enabled": true,
    "broker": "mqtt-broker-address",
    "port": 1883,
    "topic": "naga/agent/topic",
    "client_id": "naga-agent-client"
  }
}
```
</details>

---

## Ports

| Service | Port | Description |
|---------|------|-------------|
| API Server | 8000 | Main interface: chat, config, auth, Skill Market |
| Agent Server | 8001 | Task scheduling, OpenClaw |
| MCP Server | 8003 | MCP tool registration & dispatch |
| Voice Service | 5048 | TTS / ASR |
| Neo4j | 7687 | Knowledge graph (optional) |
| OpenClaw Gateway | 18789 | AI computer control (optional) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Python version error | Must use Python 3.11; recommend uv for automatic version management |
| Port in use | Check that 8000, 8001, 8003, 5048 are available |
| Neo4j timeout / hang | Fixed in 2.24; ensure Neo4j service is running |
| TTS silent / CORS error | Fixed in 2.25; confirm `voice_enabled: true` |
| Progress bar stuck | Check API Key; restart hint appears after 3 seconds |
| Floating ball avatar missing | Fixed in 2.17 (sprite frame path); confirm using latest packaged version |
| config.json garbled | Fixed in 2.19: config_manager auto-detects file encoding |
| OpenClaw fails to start | Fixed in 2.24 (missing config file in global mode) |

```bash
python main.py --check-env --force-check  # Full environment diagnostics
python main.py --quick-check              # Quick check
python update.py                          # Auto git pull + dependency sync
```

---

## Contributing

Issues and Pull Requests are welcome. For questions, join the QQ channel **nagaagent1**.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=RTGS2017/NagaAgent&type=date&legend=top-left)](https://www.star-history.com/#RTGS2017/NagaAgent&type=date&legend=top-left)

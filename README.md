# AI Council - Multi-Agent Conversational AI

A sophisticated "committee of minds" conversational AI architecture combining three specialized agents (Logical, Optimist, Critical) with an LLM-based moderator, voice input via Whisper, and avatar output via Anam AI.

## Architecture

### Cognitive Layer

-   **Agent 1 (Logical)**: Data-driven, objective analysis
-   **Agent 2 (Optimist)**: Encouraging, empathetic support
-   **Agent 3 (Critical)**: Risk assessment, devil's advocate
-   **Agent 4 (Moderator)**: LLM-based contextual selection/synthesis

### I/O Pipeline

-   **Input**: Silero VAD (client-side) → OpenAI Whisper STT (2s chunks)
-   **Output**: ElevenLabs TTS → Anam AI Avatar (pass-through mode)

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Keys Required

-   OpenAI API key (for Whisper STT and GPT-4 agents)
-   ElevenLabs API key (for TTS)
-   Anam AI API key (for avatar rendering)

## Configuration

Edit `config/agents.yaml` to customize agent personalities and system prompts.

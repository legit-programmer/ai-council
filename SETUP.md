# AI Council - Setup Guide

## Prerequisites

-   Python 3.10+
-   Node.js 18+
-   API Keys:
    -   OpenAI API key
    -   ElevenLabs API key
    -   Anam AI API key

## Backend Setup

1. **Navigate to backend directory:**

    ```bash
    cd backend
    ```

2. **Create virtual environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate virtual environment:**

    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Configure environment:**

    ```bash
    cp .env.example .env
    ```

    Edit `.env` and add your API keys:

    ```env
    OPENAI_API_KEY=sk-your-key-here
    ELEVENLABS_API_KEY=your-elevenlabs-key
    ELEVENLABS_VOICE_ID=your-voice-id
    ANAM_API_KEY=your-anam-key
    ```

6. **Run the backend:**

    ```bash
    python main.py
    ```

    Backend will start at: `http://localhost:8000`
    API docs available at: `http://localhost:8000/docs`

## Frontend Setup

1. **Navigate to frontend directory:**

    ```bash
    cd frontend
    ```

2. **Install dependencies:**

    ```bash
    npm install
    ```

3. **Configure environment:**

    ```bash
    cp .env.example .env
    ```

    Edit `.env` and add:

    ```env
    VITE_ANAM_API_KEY=your-anam-key
    ```

4. **Run the frontend:**

    ```bash
    npm run dev
    ```

    Frontend will start at: `http://localhost:3000`

## Testing

1. **Text-based query:**

    - Open `http://localhost:3000`
    - Type a message in the text input
    - Click "Send"

2. **Voice-based query:**
    - Click "Start Voice"
    - Speak your query
    - The system will automatically detect when you stop speaking
    - Wait for the avatar response

## API Endpoints

### REST API

-   `POST /api/query` - Send text query to council
-   `GET /api/history` - Get conversation history
-   `DELETE /api/history` - Clear history
-   `POST /api/anam/session` - Create Anam session token
-   `GET /api/health` - Health check

### WebSocket

-   `ws://localhost:8000/ws` - Real-time audio streaming

## Architecture Overview

### Backend Components

-   **Agents** (`backend/agents/`):

    -   `logical_agent.py` - Data-driven analysis
    -   `optimist_agent.py` - Encouraging support
    -   `critical_agent.py` - Risk assessment
    -   `moderator.py` - LLM-based selection/synthesis

-   **Graph** (`backend/graph/`):

    -   `council_graph.py` - LangGraph orchestration
    -   `state.py` - State definitions
    -   `nodes.py` - Graph node functions

-   **Memory** (`backend/memory/`):

    -   `agent_memory.py` - Per-agent memory
    -   `shared_memory.py` - Main discussion memory
    -   `memory_manager.py` - Memory coordination

-   **Pipeline** (`backend/pipeline/`):

    -   `stt.py` - Whisper speech-to-text
    -   `tts.py` - ElevenLabs text-to-speech
    -   `orchestrator.py` - Pipeline coordination

-   **API** (`backend/api/`):
    -   `routes.py` - REST endpoints
    -   `websocket.py` - WebSocket handler

### Frontend Components

-   **Hooks** (`frontend/src/hooks/`):

    -   `useVAD.ts` - Voice Activity Detection (Silero VAD, 2s chunks)
    -   `useWebSocket.ts` - WebSocket client
    -   `useAnamClient.ts` - Anam AI SDK integration

-   **Components** (`frontend/src/components/`):
    -   `AvatarDisplay.tsx` - Avatar video display

## Customization

### Agent Personalities

Edit `config/agents.yaml` to customize:

-   System prompts for each agent
-   Temperature settings
-   Model selection

### VAD Configuration

In `frontend/src/hooks/useVAD.ts`:

-   `speechThreshold` - Speech detection sensitivity (default: 0.5)
-   `silenceDuration` - Silence before end-of-speech (default: 250ms)

### Audio Chunk Size

Currently set to 2 seconds as specified. Adjust in `useVAD.ts`:

```typescript
mediaRecorder.start(2000); // 2000ms = 2 seconds
```

## Troubleshooting

### Backend Issues

1. **Import errors:**

    - Ensure virtual environment is activated
    - Run `pip install -r requirements.txt` again

2. **API key errors:**
    - Verify all keys are set in `.env`
    - Check key validity

### Frontend Issues

1. **Dependencies not found:**

    - Run `npm install` in frontend directory

2. **WebSocket connection fails:**

    - Ensure backend is running
    - Check CORS settings

3. **Avatar not loading:**
    - Verify Anam API key
    - Check browser console for errors

### Audio Issues

1. **Microphone access denied:**

    - Grant microphone permissions in browser
    - Use HTTPS in production

2. **VAD not detecting speech:**
    - Adjust `speechThreshold` in `useVAD.ts`
    - Check microphone input levels

## Production Deployment

1. **Backend:**

    - Use production WSGI server (e.g., Gunicorn)
    - Set `ENVIRONMENT=production` in `.env`
    - Configure proper CORS origins
    - Use HTTPS

2. **Frontend:**

    - Run `npm run build`
    - Serve static files with Nginx/Apache
    - Update WebSocket URL for production

3. **Security:**
    - Implement proper authentication
    - Secure API keys
    - Rate limiting
    - Input validation

## License

MIT

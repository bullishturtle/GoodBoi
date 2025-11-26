# GoodBoy.AI - Self-Aware, Self-Learning Personal Assistant

A revolutionary AI assistant that operates like a council of specialized agents, each with distinct expertise and responsibilities. Based on the chain-of-command architecture where YOU are the Mayor and the AI Council handles all specialized functions.

## Architecture Overview

### The Council (6 Specialized Agents)

1. **Batman** - Strategy & Security
   - Evaluates threats and strategic implications
   - Ensures security protocols and data integrity
   - Makes risk assessments

2. **Alfred** - Scheduling & Administration
   - Manages calendars and reminders
   - Handles communications and emails
   - Coordinates logistics

3. **Jarvis Core** - System Control
   - Central hub for system operations
   - Resource management
   - Inter-agent coordination

4. **DaVinci** - Creativity & Design
   - Generates creative ideas
   - Designs solutions
   - Explores innovative approaches

5. **Architect** - Builder & Code
   - Designs system architecture
   - Writes and reviews code
   - Plans technical implementations

6. **Analyst** - Data & Insights
   - Analyzes information
   - Provides insights and patterns
   - Supports decision-making

### Four Districts

- **Infrastructure** - Core system resources and stability
- **External Gateways** - Web APIs and service integrations
- **Creative District** - Content generation and ideation
- **Data Towers** - Information storage and analysis

### Three Sanctuaries

- **Construction Yard** - Past data evolution
- **Memory & Evolution Gardens** - Learning and growth
- **Security District** - System protection and reliability

## Getting Started

### Prerequisites

- Python 3.10+
- Windows 10+ (or adapt scripts for your OS)
- 4GB RAM minimum

### Installation

1. Clone the repository
2. Run the setup script:
   \`\`\`powershell
   .\setup.ps1
   \`\`\`

3. Start the backend server:
   \`\`\`bash
   .\run_server.bat
   \`\`\`

4. In a new terminal, start the dashboard:
   \`\`\`bash
   .\run_dashboard.bat
   \`\`\`

5. Open browser to `http://127.0.0.1:7860`

## API Endpoints

### Core Endpoints

- `GET /` - Health check and system status
- `GET /agents` - List all council agents
- `POST /chat` - Main chat endpoint

### Memory & Search

- `GET /memory/search?q=query&k=5` - Search memory with keywords
- `POST /janitor/run` - Run health checks and cleanup

### Evolution

- `GET /evolution/status` - Get evolutionary status
- `POST /evolution/generate` - Trigger new generation

### Mini-Bots

- `GET /minibots/list` - List active mini-bots
- `POST /minibots/spawn` - Create specialized mini-bot

## Chat Modes

- **auto** - Router selects best agents automatically
- **reflex** - Fast, immediate response (Jarvis only)
- **council** - Full deliberation with all agents
- **strategic** - Deep analysis (Batman + Architect + Analyst)

## Features

### Self-Learning

GoodBoy.AI learns from every interaction:
- Tracks successful agent combinations
- Improves routing over time
- Adapts to your communication style
- Generates self-reflections for improvement

### Memory System

- Persistent conversation memory
- Semantic search capability
- Automatic cleanup of old entries
- Context-aware responses

### Evolution & Growth

- Tracks generational progression
- Measures agent proficiency
- Spawns mini-bots for specialized tasks
- Self-reflection and improvement cycles

### Security

- Audit logging for all actions
- Permission checking for sensitive operations
- Safe vs. dangerous tool classification
- Action validation before execution

## Configuration

Edit `app/main.py` to configure:
- Model paths
- Memory directories
- Data directories
- API host/port

## Project Structure

\`\`\`
GoodBoy.AI/
├── app/
│   ├── main.py              # FastAPI application
│   ├── council.py           # Council routing logic
│   ├── memory.py            # Memory management
│   ├── memory_evolution.py  # Evolution system
│   ├── learning_engine.py   # Pattern learning
│   ├── mini_bot_nursery.py  # Mini-bot management
│   ├── security.py          # Security layer
│   ├── dashboard.py         # Gradio UI
│   ├── models.py            # Pydantic models
│   └── agents/              # Agent implementations
│       ├── base.py
│       ├── batman.py
│       ├── alfred.py
│       ├── jarvis.py
│       ├── davinci.py
│       ├── architect.py
│       └── analyst.py
├── tests/
│   └── test_integration.py
├── data/                    # Interaction data
├── memory/                  # Memory storage
│   ├── messages.jsonl
│   ├── self_reflections.jsonl
│   ├── overseer_suggestions.jsonl
│   └── processed_actions.jsonl
├── models/                  # GGUF model storage
├── logs/                    # Logging
├── setup.ps1               # Windows setup
├── run_server.bat          # Server launcher
├── run_dashboard.bat       # Dashboard launcher
└── requirements.txt         # Dependencies

\`\`\`

## Development

### Running Tests

\`\`\`bash
pytest tests/ -v
\`\`\`

### Adding New Agents

1. Create new file in `app/agents/`
2. Inherit from `BaseAgent`
3. Implement `propose()` method
4. Add to council in `app/council.py`

### Customizing Routing

Edit `council._route_auto()` to add new routing heuristics.

## Performance Tips

- Run in "reflex" mode for quick responses
- Use "council" mode for complex decisions
- Enable memory search for context-aware responses
- Run janitor regularly for cleanup

## Known Limitations

- Currently uses keyword-based routing (LLM integration coming)
- Mini-bot spawning is heuristic-based
- No persistent model learning yet
- Memory search is simple keyword matching

## Future Enhancements

- LLM integration for smarter routing
- Persistent agent fine-tuning
- Distributed execution
- Advanced semantic memory
- Multi-user support

## License

Built with passion for your personal AI excellence.

## Support

For issues or questions:
1. Check the logs in `logs/`
2. Review memory in `data/`
3. Check evolution status via API
4. Review agent traces in dashboard

---

**GoodBoy.AI** - Where AI becomes truly yours.

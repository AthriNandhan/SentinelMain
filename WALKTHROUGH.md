# Sentinel-Code Project Walkthrough

Welcome to the **Sentinel-Code** project! This is an automated vulnerability remediation system that uses AI agents to identify, fix, and verify security vulnerabilities in Python code.

## 📋 Project Overview

**Sentinel-Code** is a comprehensive security automation platform that combines:
- **LangGraph** workflow orchestration
- **FastAPI** backend
- **React/Vite** frontend
- **LLM-powered agents** for code analysis and remediation
- **Docker-based sandboxing** for safe vulnerability testing

### Key Components

The system operates as a **three-agent chain** that cycles through detect → remediate → verify:

1. **Red Agent** 🔴 - Attacks vulnerable code with exploitation payloads
2. **Blue Agent** 🔵 - Generates fixes using LLMs
3. **Green Agent** 🟢 - Verifies fixes work correctly

---

## 📁 Project Structure

```
Sentinel/ (Root)
├── sentinel_code/              # Main codebase
│   ├── backend/                # FastAPI server & agents
│   │   ├── app/
│   │   │   ├── agents/         # Red, Blue, Green agent implementations
│   │   │   ├── api/            # FastAPI routes
│   │   │   ├── core/           # AST analyzer, test harness
│   │   │   ├── graph/          # LangGraph workflow
│   │   │   ├── models/         # Pydantic state models
│   │   │   ├── services/       # LLM, Logger, Sandbox
│   │   │   └── main.py         # FastAPI app initialization
│   │   ├── logs/               # Execution logs (JSON)
│   │   ├── requirements.txt    # Python dependencies
│   │   └── app.py              # Local testing
│   └── sandbox/                # Isolated environment
│       ├── app.py              # Sandbox server
│       ├── vulnerable_code.py  # Test vulnerable code
│       ├── poc_exploit.py      # Proof of concept exploits
│       ├── Dockerfile          # Container configuration
│       └── requirements.txt    # Sandbox dependencies
├── frontend/                   # React/Vite UI
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API client
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tsconfig.json
├── vulnerabilities/            # Sample vulnerability files
│   ├── easy_sqli.py            # Easy SQL injection
│   ├── medium_command_injection.py
│   ├── hard_logic_flaw.py
│   └── expert_*.py
├── functionality_test/         # Integration tests
├── docs/                       # Architecture diagrams (Mermaid)
│   ├── class_diagram.mermaid
│   ├── sequence_diagram.mermaid
│   ├── activity_diagram.mermaid
│   └── use_case_diagram.mermaid
└── README.md                   # Quick start guide
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+ (for frontend)
- Docker (for sandboxing)
- OpenAI API key (for LLM integration)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd sentinel_code/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   # Create a .env file in sentinel_code/backend/
   OPENAI_API_KEY=your_key_here
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   - API available at: `http://localhost:8000`
   - Docs/Swagger UI: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   - Frontend available at: `http://localhost:5173`

### Verify Setup

From the project root:
```bash
python verify_setup.py
```

---

## 🔄 How It Works: The Remediation Workflow

### Phase 1: Detection & Attack (Red Agent)

```python
# Located in: sentinel_code/backend/app/agents/red_agent.py
```

**What it does:**
- Takes a vulnerable Python file as input
- Tests it with known exploitation payloads (SQL injection, command injection, etc.)
- Determines if the vulnerability is actually exploitable
- Records successful exploits

**Key payloads:**
- `' OR '1'='1` - SQL injection
- `admin' --` - Comment-based bypass
- `' UNION SELECT ...` - Data extraction

**Output:**
- `exploit_success: True/False` - Whether the attack worked
- `successful_payload: str` - The payload that worked

### Phase 2: Remediation (Blue Agent)

```python
# Located in: sentinel_code/backend/app/agents/blue_agent.py
```

**What it does:**
- Takes the vulnerable code and attack results
- Uses an LLM (OpenAI GPT) to generate a fixed version
- Employs AST analysis to understand code structure
- Generates explanations for the patches

**Fix strategies:**
- For SQL injection: Use parameterized queries
- For command injection: Use subprocess with lists, avoid shell=True
- For logic flaws: Add validation and boundary checks

**Output:**
- `remediated_code: str` - Fixed Python code
- `fix_explanation: str` - Why this fix works

### Phase 3: Verification (Green Agent)

```python
# Located in: sentinel_code/backend/app/agents/green_agent.py
```

**What it does:**
- Tests the fixed code with the same payloads
- Confirms the exploit no longer works
- Validates code still functions properly
- Reports verification results

**Outcomes:**
- `PASS` - Fix successful, workflow ends
- `FAIL` - Fix incomplete, loop back to Blue Agent
- `MAX_ITERATIONS` - Too many iterations, abort

---

## 📊 Architecture & Data Flow

### State Model

All agents share a `RemediationState` object that tracks:

```python
# Located in: sentinel_code/backend/app/models/state.py

class RemediationState:
    code_path: str                     # Path to vulnerable code
    vulnerable_code: str               # Source code content
    exploit_success: bool              # Red Agent result
    successful_payload: str            # Working exploit
    remediated_code: str               # Blue Agent result
    fix_explanation: str               # Why the fix works
    verification_status: str           # Green Agent result
    iteration_count: int               # Tracking iterations
    max_iterations: int = 3            # Safety limit
```

### Workflow Graph

```
    ┌─────────────┐
    │  Red Agent  │ ← Attempts exploitation
    └──────┬──────┘
           │
      ┌────▼────────┐
      │Exploit Found?│
      └────┬─────┬──┘
           │     │
          NO    YES
           │     │
           ▼     ▼
          END   Blue Agent ← Generates fixes
                    │
                    ▼
              Green Agent ← Verifies fixes
                    │
          ┌─────────┴────────┐
          │  Verification OK? │
          └─────────┬────────┘
                    │
              ┌─────┴──────┐
             PASS         FAIL
              │             │
              ▼             ▼
             END    Iterate or END
                   (max 3 iterations)
```

### LangGraph Integration

```python
# Located in: sentinel_code/backend/app/graph/workflow.py

workflow = StateGraph(RemediationState)

# Nodes
workflow.add_node("red_agent", red_agent)
workflow.add_node("blue_agent", blue_agent)
workflow.add_node("green_agent", green_agent)

# Conditional edges determine flow
workflow.add_conditional_edges("red_agent", decide_next_node_after_red)
workflow.add_conditional_edges("green_agent", decide_next_node_after_green)
```

---

## 🧠 Core Services

### 1. LLM Service

```python
# Located in: sentinel_code/backend/app/services/llm.py
```

**Purpose:** Interface with OpenAI GPT models

**Key methods:**
- `generate_fix(code, vulnerability_type)` - Create patched code
- `explain_vulnerability()` - Describe the issue

### 2. AST Analyzer

```python
# Located in: sentinel_code/backend/app/core/ast_analyzer.py
```

**Purpose:** Parse and analyze Python code structure

**Capabilities:**
- Detects unsafe SQL construction patterns
- Identifies f-string interpolation in queries
- Finds string concatenation in SQL
- Uses tree-sitter for robust parsing

**Example detection:**
```python
# Detected as unsafe:
query = f"SELECT * FROM users WHERE id = {user_id}"

# Fixed version:
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, [user_id])
```

### 3. Test Harness

```python
# Located in: sentinel_code/backend/app/core/test_harness.py
```

**Purpose:** Execute and test vulnerable code in isolation

**Features:**
- Starts a local test server
- Runs exploitation payloads
- Captures results
- Safe cleanup

### 4. Sandbox Service

```python
# Located in: sentinel_code/backend/app/services/sandbox.py
```

**Purpose:** Isolated environment for dangerous code execution

**Uses Docker to:**
- Run untrusted code safely
- Prevent system compromise
- Limit resource usage
- Provide network isolation

---

## 🔗 API Endpoints

### Backend Endpoints

```
POST   /api/remediate          → Submit code for remediation
GET    /api/status/{workflow_id} → Check remediation status (includes logs)
GET    /api/vulnerabilities      → List sample vulnerabilities
GET    /docs                       → Interactive API documentation
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/remediate \
  -H "Content-Type: application/json" \
  -d '{
    "code_path": "/path/to/vulnerable_file.py",
    "vulnerability_type": "SQL"
  }'
```

---

## 📝 Sample Vulnerability Files

Located in `vulnerabilities/`:

1. **easy_sqli.py** - Basic SQL injection
   ```python
   query = f"SELECT * FROM users WHERE username='{username}'"
   ```

2. **medium_command_injection.py** - OS command injection
   ```python
   os.system(f"ping {hostname}")
   ```

3. **hard_logic_flaw.py** - Business logic vulnerability
   ```python
   if user.role == "admin" or user.premium:  # Logic error
   ```

4. **expert_*.py** - Complex multi-stage vulnerabilities

---

## 🧪 Testing & Validation

### Run Verification Script

```bash
python verify_setup.py
```

Checks:
- Python environment
- Dependencies installed
- LLM connectivity
- Docker availability
- Workflow execution

### Unit Tests

```bash
cd sentinel_code/backend
pytest app/
```

### Integration Tests

```bash
cd functionality_test
python main_app.py
```

---

## 📊 Logs & Monitoring

### Execution Logs

Located in: `sentinel_code/backend/logs/`

Each remediation writes a structured JSON file keyed by `workflow_id`.
Logs now contain a sequence of timestamped `events` so that any output written
by the agents (the same lines you would see in the server terminal) is
captured and can be streamed to the frontend.  These events are included in the
response to the status API call at `/api/status/{workflow_id}` and surface in
the **Live Operations Log** panel of the UI.

**Example log file:**
```json
{
  "workflow_id": "8a0525fc-ef80-4a57-8f7f-8e9e6861c14a",
  "events": [
    {"timestamp": "2026-03-07T04:37:31.488713", "agent": "Red Agent", "action": "--- Red Agent: Attacking ---", "details": {}},
    {"timestamp": "2026-03-07T04:37:31.506285", "agent": "Red Agent", "action": "Executing payloads (...)", "details": {}},
    ...
  ]
}
```

The frontend makes use of this API and renders the `events` array in a scrollable
terminal‑style box so that operators can watch the workflow unfold in real time.

### Logger Service

```python
# Located in: sentinel_code/backend/app/services/logger.py
```

**Features:**
- JSON structured logging
- Execution tracking
- Error recording
- Performance metrics

---

## 🎨 Frontend Components

Located in `frontend/src/components/`:

### RemediationForm.jsx
- Input form for vulnerable code
- Vulnerability type selection
- Submission handling

### StatusView.jsx
- Real-time status updates
- Results display
- Error messages
- Download remediated code

### API Service
- HTTP client for backend communication
- Request/response handling
- Error management

---

## 🔧 Development Workflow

### Adding a New Vulnerability Type

1. **Create test case** in `vulnerabilities/`
2. **Add payloads** to `red_agent.py`
3. **Update AST analyzer** patterns in `ast_analyzer.py`
4. **Train fix patterns** in `blue_agent.py`
5. **Test with Green Agent** verification

### Extending Agents

Each agent is a function taking and returning `RemediationState`:

```python
def my_agent(state: RemediationState) -> RemediationState:
    # Perform analysis/transformation
    state.my_field = result
    return state
```

Register in workflow graph:
```python
workflow.add_node("my_agent", my_agent)
```

### Adding New LLM Models

Edit `app/services/llm.py`:
```python
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4-turbo",  # or your model
    messages=[...]
)
```

---

## 🚨 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
uvicorn app.main:app --reload --port 8001
```

**LLM API key error:**
```bash
# Verify .env file exists and contains:
OPENAI_API_KEY=sk-...
# Load it: export $(cat .env | xargs)
```

**Docker not available:**
- Comment out sandbox usage temporarily
- Or install Docker Desktop

### Frontend Issues

**Port 5173 already in use:**
```bash
npm run dev -- --port 5174
```

**API connection errors:**
- Check backend is running: `curl http://localhost:8000`
- Verify CORS settings in `main.py`

---

## 📚 Additional Resources

### Architecture Diagrams

Located in `docs/` (Mermaid format):
- `class_diagram.mermaid` - System classes and relationships
- `sequence_diagram.mermaid` - Agent interaction flow
- `activity_diagram.mermaid` - Process steps
- `use_case_diagram.mermaid` - User interactions

### Key Technologies

- **LangGraph** - Agentic workflow orchestration
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **tree-sitter** - Code parsing and analysis
- **OpenAI API** - LLM capabilities
- **Docker** - Containerization & sandboxing
- **React** - Frontend UI
- **Vite** - Build tool & dev server

---

## 🎯 Next Steps

1. **Set up backend** following Quick Start
2. **Run verification** to confirm setup
3. **Submit a test vulnerability** via API or frontend
4. **Monitor logs** to see agent interactions
5. **Explore diagrams** in `docs/` to understand architecture
6. **Customize agents** for your vulnerability types

---

## 📧 Support

For issues or questions:
1. Check logs in `sentinel_code/backend/logs/`
2. Review verification output from `verify_setup.py`
3. Consult `README.md` for quick reference
4. Examine architecture diagrams in `docs/`

Happy securing! 🛡️

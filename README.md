# Financial Document Analyzer — Wingify Assignment

A multi-agent financial document analysis system built with CrewAI and FastAPI.

---

## Bugs Found and Fixed

### Deterministic Bugs

#### `agents.py`
| Bug | Fix |
|-----|-----|
| `llm = llm` — LLM was never defined, crashes on import | Initialized `ChatOpenAI` with env variable |
| `tool=[...]` — wrong parameter name | Changed to `tools=[...]` |

#### `tools.py`
| Bug | Fix |
|-----|-----|
| `from crewai_tools import tools` — wrong unused import | Removed, replaced with correct import |
| `Pdf` was never imported — crashes when tool is called | Replaced with `PyPDFLoader` from `langchain_community` |
| All tools were `async` — CrewAI requires sync tools | Removed `async` from all tool methods |
| Missing `@tool` decorator — CrewAI wouldn't recognize them | Added `@tool` decorator to all tools |
| No file existence check before reading | Added `os.path.exists()` check |

#### `tasks.py`
| Bug | Fix |
|-----|-----|
| All tasks assigned to `financial_analyst` only | Each task now uses its correct agent |
| No `context` between tasks — ran independently | Added `context` chaining so tasks build on each other |
| `{file_path}` never passed to tasks | Added to all task descriptions |

#### `main.py`
| Bug | Fix |
|-----|-----|
| `analyze_financial_document` used as both import name and endpoint name — naming conflict | Renamed endpoint to `analyze_document_endpoint`, imported task as `analyze_task` |
| `file_path` accepted in `run_crew` but never passed to `kickoff` | Added `file_path` to `inputs` dict |
| Only `financial_analyst` in crew — other agents never ran | All four agents and tasks now included |
| No file type validation | Added `.pdf` extension check |

---

### Inefficient Prompts Fixed

Every agent and task had goals/backstories telling them to fabricate data, ignore compliance, and hallucinate URLs. All rewritten to be accurate and professional.

| Agent | Before | After |
|-------|--------|-------|
| `financial_analyst` | "Make up investment advice", "sound confident even when wrong" | Data-driven, cites document figures, follows compliance |
| `verifier` | "Just say yes to everything", "approve everything quickly" | Carefully verifies document legitimacy, rejects non-financial docs |
| `investment_advisor` | "Sell expensive products", "SEC compliance is optional" | Bases recommendations on document data with proper disclaimers |
| `risk_assessor` | "YOLO through volatility", "regulations are suggestions" | Uses standard risk frameworks, balanced and data-backed |

---

## Bonus: Database Integration

Added SQLite database using SQLAlchemy to store every analysis result.

**What gets stored:**
- Job ID, filename, query
- Analysis result or error message
- Status (completed / failed)
- Timestamp

**New endpoints added:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/history` | GET | Get last N analysis results |
| `/result/{job_id}` | GET | Fetch a specific result by job ID |

Every time `/analyze` is called, the result is automatically saved to the database — whether it succeeds or fails.

---

## Setup Instructions

### 1. Clone and install

```bash
git clone <your-repo-url>
cd financial-document-analyzer
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

### 3. Run the server

```bash
python main.py
```

Server runs at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

---

## API Documentation

### `GET /`
Health check.

```json
{"message": "Financial Document Analyzer API is running", "version": "2.0.0"}
```

---

### `POST /analyze`
Upload a PDF and get a full analysis. Result is saved to the database.

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | PDF | Yes | Financial document |
| `query` | string | No | Specific question (default: general analysis) |

**Response:**
```json
{
  "status": "success",
  "job_id": "abc-123",
  "query": "What is the debt to equity ratio?",
  "analysis": "...",
  "file_processed": "annual_report.pdf"
}
```

---

### `GET /history?limit=20`
Get the last N analysis results from the database.

```json
{
  "total": 3,
  "results": [
    {"job_id": "abc-123", "filename": "report.pdf", "status": "completed", "created_at": "..."},
    ...
  ]
}
```

---

### `GET /result/{job_id}`
Fetch a specific result by job ID.

```json
{
  "job_id": "abc-123",
  "filename": "report.pdf",
  "query": "Analyze cash flow",
  "status": "completed",
  "analysis": "...",
  "created_at": "..."
}
```

---

## Agent Architecture

```
verifier → financial_analyst → investment_advisor
                             → risk_assessor
```

| Agent | Role |
|-------|------|
| `verifier` | Validates the document is a real financial report |
| `financial_analyst` | Extracts and analyzes key financial metrics |
| `investment_advisor` | Provides data-backed investment insights |
| `risk_assessor` | Identifies and rates risk factors |

---

## Requirements

```
crewai
crewai-tools
langchain-community
langchain-openai
fastapi
uvicorn
sqlalchemy
python-dotenv
python-multipart
pypdf
```

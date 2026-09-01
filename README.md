# AI Coding Agent

An AI-powered coding agent built with **Python, LangChain, LangGraph, and Ollama**.

The agent understands coding requests, creates implementation plans, generates and modifies Python files using tools, requests human approval before tool execution, performs functional testing, and uses bounded self-repair to fix failed implementations.

## Features

* 🧠 **Planning** — Creates a step-by-step implementation plan.
* 💻 **Code Generation** — Generates and modifies Python files using a local LLM.
* 🛠️ **Tool Calling** — Uses file-management tools to interact with the workspace.
* 👤 **Human-in-the-Loop** — Requests approval before executing tools.
* 🧪 **Automated Testing** — Executes generated Python programs and captures output/errors.
* ✅ **Functional Testing** — Compares expected and actual output.
* 🔧 **Self-Repair** — Attempts to fix code when testing fails.
* 🔁 **Bounded Repair** — Limits repair attempts to prevent endless loops.
* 💾 **Checkpointing** — Uses LangGraph checkpointing to maintain workflow state.
* 📊 **LangSmith** — Provides tracing and observability for the agent workflow.
* 🏠 **Local LLM** — Uses Ollama instead of a cloud-based LLM API.

---

## Architecture

```text
                         USER
                           │
                           ▼
                       PLANNER
                           │
                           ▼
                         CODER
                           │
                    Tool required?
                     /          \
                   YES           NO
                    │             │
                    ▼             ▼
                  HITL          TESTER
                    │          /       \
                    ▼        PASS      FAIL
                  TOOLS        │         │
                    │          ▼         ▼
                    └──────►  END      REPAIR
                                         │
                                         ▼
                                       CODER
                                         │
                                         ▼
                                       TESTER
```

Maximum repair attempts: **3**

---

## How It Works

### 1. User Request

The user provides a coding task.

Example:

```text
Create a Python file called calculator.py with a function add(a, b)
that returns the sum of two numbers, and print the result of adding 5 and 3.
```

### 2. Planner

The planner converts the request into a simple implementation plan.

Example:

```text
1. Create calculator.py
2. Define add(a, b)
3. Return a + b
4. Print add(5, 3)

EXPECTED OUTPUT: 8
```

### 3. Coder

The coder receives:

* User request
* Implementation plan
* Previous test result
* Conversation/tool messages

It can use:

```text
list_files
read_file
write_file
```

### 4. Human-in-the-Loop

Before a tool is executed, the agent pauses and asks for approval.

Example:

```text
--- HUMAN APPROVAL ---

Tool: write_file
Arguments:
{
    "filename": "calculator.py",
    "content": "..."
}

Allow this tool? (yes/no):
```

If approved, the tool executes.

If rejected, the request is returned to the coder.

### 5. Testing

The tester:

1. Checks whether the file exists.
2. Executes the Python program.
3. Captures standard output and errors.
4. Checks for runtime failures.
5. Compares actual output with the expected output.

Example:

```text
Expected: 8
Actual: 8

PASS
```

### 6. Self-Repair

If the program produces an incorrect result:

```text
Expected: 8
Actual: 2
```

the workflow enters the repair process:

```text
FAIL
  ↓
REPAIR
  ↓
CODER
  ↓
read_file
  ↓
write_file
  ↓
TESTER
```

The agent can make up to **3 repair attempts**.

---

## Technologies

| Technology | Purpose                             |
| ---------- | ----------------------------------- |
| Python     | Core application                    |
| LangChain  | LLM and tool integration            |
| LangGraph  | Agent workflow and state management |
| Ollama     | Local LLM execution                 |
| LangSmith  | Tracing and observability           |
| TypedDict  | Agent state definition              |

---

## Project Structure

```text
ai-coding-agent/
│
├── src/
│   └── ai_coding_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── graph.py
│       ├── state.py
│       ├── tools.py
│       └── tester.py
│
├── workspace/
│   └── .gitkeep
│
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

### File Responsibilities

- **`main.py`** — Handles user interaction, graph execution, and human approval.
- **`graph.py`** — Defines the LangGraph workflow, planner, coder, HITL, tools, tester, and repair logic.
- **`state.py`** — Defines the shared state used throughout the workflow.
- **`tools.py`** — Contains `list_files`, `read_file`, and `write_file`.
- **`tester.py`** — Executes generated Python files and performs runtime and functional testing.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/GreshmaMotupalli/ai-coding-agent.git

cd ai-coding-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama

Install and run Ollama, then pull the model configured for the project.

Example:

```bash
ollama pull qwen3:4b
```

Set the model in `.env`:

```env
OLLAMA_MODEL=qwen3:4b
```

### 5. Configure LangSmith

Add your LangSmith configuration to `.env`:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=ai-coding-agent
```

Never commit your real API key to GitHub.

### 6. Run the agent

From the project environment:

```bash
cd src/ai_coding_agent
python main.py
```

---

## Example Execution

```text
You: Create a Python file called calculator.py with a function
add(a, b) that returns the sum of two numbers, and print the
result of adding 5 and 3.

--- PLANNER ---

EXPECTED OUTPUT: 8

--- CODER ITERATION 1 ---

--- HUMAN APPROVAL ---

Tool: write_file

Allow this tool? (yes/no): yes

Tool approved.

--- CODER ITERATION 2 ---

--- TESTER ---

PASS
Expected: 8
Actual: 8

--- FINAL RESULT ---

PASS
Expected: 8
Actual: 8
File: calculator.py
Repair attempts: 0
```

---

## Self-Repair Example

When generated code produces an incorrect result, the agent enters
a bounded repair loop.

```text
--- TESTER ---

FAIL
Expected: 8
Actual: 2

--- REPAIR ATTEMPT 1 ---

--- CODER ITERATION 3 ---

The coder receives the previous test result and attempts to fix the code.

--- TESTER ---

PASS
Expected: 8
Actual: 8

--- FINAL RESULT ---

PASS
Expected: 8
Actual: 8
File: calculator.py
Repair attempts: 1
```

---

## Screenshots

### Agent Execution

<img width="1258" height="745" alt="image" src="https://github.com/user-attachments/assets/92257a30-3655-4aca-8fdb-003c429ba45e" />


### Self-Repair

<img width="454" height="386" alt="image" src="https://github.com/user-attachments/assets/a9543456-7c38-41f3-8397-e296fe798b7c" />


### LangSmith Trace

<img width="892" height="359" alt="image" src="https://github.com/user-attachments/assets/2e8fdeb3-f432-4247-bcb1-ac49bf3c4d11" />



---

## LangSmith

LangSmith is used to observe and debug the agent workflow.

A trace can show the sequence of operations:

```text
Planner
   ↓
Coder
   ↓
Tool Call
   ↓
Human Approval
   ↓
Tool Execution
   ↓
Coder
   ↓
Tester
   ↓
Repair (if required)
```

This makes it easier to understand how the LangGraph agent executes each task.

---

## Key Learning Outcomes

This project demonstrates practical understanding of:

* LangChain
* LangGraph
* State-based agent workflows
* LLM tool calling
* Human-in-the-loop workflows
* LangGraph checkpointing
* Automated code execution
* Functional testing
* Error-driven self-repair
* Bounded agent loops
* Local LLMs with Ollama
* LangSmith observability

---

## Future Improvements

Possible future improvements include:

* More robust test-case generation
* Support for additional programming languages
* Better code validation
* Improved error classification
* More detailed execution reports

The current project intentionally focuses on a **simple and understandable coding-agent architecture** rather than adding unnecessary complexity.

---

## Author

**Greshma Motupalli**

GitHub: [GreshmaMotupalli](https://github.com/GreshmaMotupalli)

import os

from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import (ChatPromptTemplate,MessagesPlaceholder)
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from ai_coding_agent.state import CodingState

from ai_coding_agent.tools import (
    write_file,
    read_file,
    list_files,
)
from ai_coding_agent.tester import tester

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# LLM
# =====================================================

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL"),
    temperature=0,
)


# =====================================================
# TOOLS
# =====================================================

tools = [
    write_file,
    read_file,
    list_files,
]


# Give tools to the LLM
llm_with_tools = llm.bind_tools(tools)


# =====================================================
# PLANNER
# =====================================================

def planner(state: CodingState):

    print("\n--- PLANNER ---")

    planner_prompt = f"""
You are a software development planner.

The user wants:

{state["user_request"]}

Create a simple step-by-step implementation plan.

Rules:
- Understand the user's requirement.
- Break it into logical steps.
- Keep the plan simple.
- Do not write code.
"""

    response = llm.invoke(planner_prompt)

    print("\nPLAN:")
    print(response.content)

    return {
        "plan": response.content
    }


# =====================================================
# CODER PROMPT
# =====================================================
coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert Python coding agent.

You are working inside a workspace directory.

User request:

{user_request}

Implementation plan:

{plan}

Previous test result:

{test_result}

You have access to these tools:

1. list_files
   Use this to see what files exist.

2. read_file
   Use this to read an existing file.

3. write_file
   Use this to create or modify a file.

Rules:

- If you need to see available files, use list_files.
- If you need to inspect an existing file, use read_file.
- If you need to create or modify a file, use write_file.
- Never assume the contents of an existing file.
- Files must be inside the workspace.
- If the previous test failed, inspect the error and fix the problem.
- After fixing the problem, use write_file to update the file.
- Complete the user's request.
"""
        ),

        MessagesPlaceholder(
            variable_name="messages"
        ),
    ]
)
# =====================================================
# CODER CHAIN
# =====================================================

coder_chain = coder_prompt | llm_with_tools


# =====================================================
# CODER NODE
# =====================================================
def coder(state: CodingState):

    iteration = state.get("iteration", 0) + 1

    print(f"\n--- CODER ITERATION {iteration} ---")

    response = coder_chain.invoke(
        {
            "user_request": state["user_request"],
            "plan": state["plan"],
            "test_result": state.get("test_result", ""),
            "messages": state["messages"],
        }
    )

    filename = state.get("filename", "")

    if response.tool_calls:

        for tool_call in response.tool_calls:

            if tool_call["name"] == "write_file":

                filename = tool_call["args"].get(
                    "filename",
                    filename
                )

    return {
        "messages": [response],
        "code": response.content,
        "filename": filename,
        "iteration": iteration,
    }
# =====================================================
# HUMAN APPROVAL NODE
# =====================================================

def approval_node(state: CodingState):

    print("\n--- HUMAN APPROVAL ---")

    last_message = state["messages"][-1]

    tool_call = last_message.tool_calls[0]

    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    approval = interrupt(
        {
            "message": "The agent wants to use a tool.",
            "tool": tool_name,
            "arguments": tool_args,
        }
    )

    if approval == "yes":

        print("\nTool approved.")

        return Command(
            goto="tools"
        )

    print("\nTool rejected.")

    return Command(
        goto="coder",
        update={
            "messages": [
                {
                    "role": "assistant",
                    "content": (
                        f"Human rejected the tool call: {tool_name}. "
                        "Do not use this tool call. "
                        "Choose another approach."
                    ),
                }
            ]
        },
    )
# =====================================================
# TOOL NODE
# =====================================================

tool_node = ToolNode(tools)


# =====================================================
# ROUTER
# =====================================================
def route_after_coder(state: CodingState):

    MAX_ITERATIONS = 5

    if state["iteration"] >= MAX_ITERATIONS:
        return "tester"

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "approval"

    if state.get("filename"):
        return "tester"

    return END

def route_after_tester(state: CodingState):

    test_result = state.get("test_result", "")

    if test_result.startswith("PASS"):
        return END

    return "coder"

# =====================================================
# BUILD GRAPH
# =====================================================

builder = StateGraph(CodingState)


builder.add_node(
    "planner",
    planner
)

builder.add_node(
    "coder",
    coder
)

builder.add_node(
    "approval",
    approval_node
)

builder.add_node(
    "tools",
    tool_node
)

builder.add_node(
    "tester",
    tester
)

# START → PLANNER

builder.add_edge(
    START,
    "planner"
)


# PLANNER → CODER

builder.add_edge(
    "planner",
    "coder"
)


# CODER → APPROVAL or END

builder.add_conditional_edges(
    "coder",
    route_after_coder,
    {
        "approval": "approval",
        "tester": "tester",
        END: END,
    }
)

builder.add_conditional_edges(
    "tester",
    route_after_tester,
    {
        "coder": "coder",
        END: END,
    }
)

# TOOLS → CODER

builder.add_edge(
    "tools",
    "coder"
)

# =====================================================
# COMPILE GRAPH
# =====================================================

memory = InMemorySaver()

graph = builder.compile(
    checkpointer=memory
)

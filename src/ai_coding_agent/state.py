from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class CodingState(TypedDict):
    user_request: str
    plan: str
    code: str
    filename: str
    test_result: str
    iteration: int

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

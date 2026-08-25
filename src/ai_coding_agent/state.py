from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CodingState(TypedDict):
    user_request: str
    plan: str
    code: str

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]
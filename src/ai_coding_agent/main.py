from langgraph.types import Command

from ai_coding_agent.graph import graph


config = {
    "configurable": {
        "thread_id": "user-1"
    }
}


while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    initial_state = {
        "user_request": user_input,
        "plan": "",
        "code": "",
        "messages": [],
    }

    result = graph.invoke(
        initial_state,
        config=config
    )

    # -----------------------------------------------
    # GRAPH WAS INTERRUPTED
    # -----------------------------------------------

    if "__interrupt__" in result:

        interrupt_info = result["__interrupt__"][0].value

        print("\n⚠️ HUMAN APPROVAL REQUIRED")

        print("Tool:", interrupt_info["tool"])

        print("Arguments:", interrupt_info["arguments"])

        answer = input("\nAllow this tool? (yes/no): ")

        result = graph.invoke(
            Command(resume=answer.lower()),
            config=config
        )

    print("\nAgent:")

    if result.get("code"):
        print(result["code"])

    else:
        print("Request completed.")
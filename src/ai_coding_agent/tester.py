import subprocess
from pathlib import Path

from ai_coding_agent.state import CodingState


WORKSPACE = Path("workspace")


def tester(state: CodingState):

    print("\n--- TESTER ---")

    filename = state["filename"]

    if not filename:
        return {
            "test_result": "FAIL: No filename was provided."
        }

    file_path = WORKSPACE / filename

    if not file_path.exists():
        return {
            "test_result": (
                f"FAIL: File '{filename}' does not exist."
            )
        }

    try:

        result = subprocess.run(
            ["python", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:

            return {
                "test_result": (
                    "PASS\n"
                    f"Output:\n{result.stdout}"
                )
            }

        else:

            return {
                "test_result": (
                    "FAIL\n"
                    f"Error:\n{result.stderr}"
                )
            }

    except subprocess.TimeoutExpired:

        return {
            "test_result": "FAIL: Program timed out."
        }

    except Exception as e:

        return {
            "test_result": f"FAIL: {str(e)}"
        }
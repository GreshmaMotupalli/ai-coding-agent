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

        # Program crashed
        if result.returncode != 0:

            return {
                "test_result": (
                    "FAIL\n"
                    f"Error:\n{result.stderr}"
                )
            }

        actual_output = result.stdout.strip()

        expected_output = state.get("expected_output", "").strip()

        # No expected output was provided
        if not expected_output:

            return {
                "test_result": (
                    "PASS\n"
                    f"Output:\n{actual_output}"
                )
            }

        # Functional test
        if actual_output == expected_output:

            return {
                "test_result": (
                    "PASS\n"
                    f"Expected: {expected_output}\n"
                    f"Actual: {actual_output}"
                )
            }

        # Program ran but produced the wrong result
        return {
            "test_result": (
                "FAIL\n"
                f"Expected: {expected_output}\n"
                f"Actual: {actual_output}"
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

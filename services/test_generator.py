import os
import re
import uuid
import subprocess
import json
from datetime import datetime


def create_pipeline_folder(base_path: str = "data") -> str:
    """
    Create a unique folder for storing pipeline files
    """
    pipeline_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{pipeline_id}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def save_input_code(input_code: str, folder_path: str) -> str:
    """
    Save the input code to a file in the pipeline folder
    """
    input_file = os.path.join(folder_path, "main.py")
    with open(input_file, "w") as f:
        f.write(input_code)
    return input_file


def write_test_python_file(code_string: str, folder_path: str, file_name: str = "test"):
    """
    Extract Python code from API response and write it to a file in the pipeline folder
    """
    code_match = re.search(r"```python\n(.*?)```", code_string, re.DOTALL)

    if code_match:
        unit_test_code = code_match.group(1).strip()

        output_file = os.path.join(folder_path, f"{file_name}.py")

        with open(output_file, "w") as f:
            f.write(unit_test_code)

        return output_file
    else:
        return None


def run_test_file(test_file_path: str, folder_path: str) -> dict:
    """
    Run the test file using pytest and return the results
    """
    try:
        test_filename = os.path.basename(test_file_path)

        result = subprocess.run(
            ["python", "-m", "pytest", test_filename, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=folder_path,
        )

        test_results = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat(),
        }

        results_file = os.path.join(folder_path, "test_results.json")
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2)

        return test_results

    except Exception as e:
        error_results = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

        results_file = os.path.join(folder_path, "test_results.json")
        with open(results_file, "w") as f:
            json.dump(error_results, f, indent=2)

        return error_results

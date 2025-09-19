import os
import re


def write_test_python_file(
    code_string: str, file_name: str = "test", file_path: str = "data"
):
    """
    Extract Python code from API response and write it to a file
    """
    code_match = re.search(r"```python\n(.*?)```", code_string, re.DOTALL)

    if code_match:
        unit_test_code = code_match.group(1).strip()

        os.makedirs(file_path, exist_ok=True)
        output_file = os.path.join(file_path, f"{file_name}.py")

        with open(output_file, "w") as f:
            f.write(unit_test_code)

        return f"Unit test saved to {output_file}"
    else:
        return "No Python code found in response"

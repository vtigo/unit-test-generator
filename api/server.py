from fastapi import FastAPI

from llm import AnthropicEngine, prompts
from utils.file import (
    write_test_python_file,
    create_pipeline_folder,
    save_input_code,
    run_test_file,
)

from .types import MessageRequest

UnitTestAgent = AnthropicEngine(system=prompts.unit_test_generator)

app = FastAPI()

# TODO: save to a folder (with id) inside data, where we store:
# 1. the inputed code
# 2. the unit test
# 3. the results
# for the specific pipeline


@app.post("/generate_test_file")
def generate_test_file(request: MessageRequest):
    # Create a unique folder for this pipeline
    folder_path = create_pipeline_folder()

    # Save the input code
    input_file = save_input_code(request.content, folder_path)

    # Generate the unit test
    response = UnitTestAgent.send_message(request.content)

    if isinstance(response, list) and len(response) > 0:
        text_content = response[0].text
    else:
        text_content = str(response)

    # Save the unit test in the same folder
    test_file_path = write_test_python_file(text_content, folder_path)

    if test_file_path:
        # Run the test and get results
        test_results = run_test_file(test_file_path, folder_path)

        return {
            "message": f"Unit test saved to {test_file_path}",
            "folder": folder_path,
            "input_file": input_file,
            "test_file": test_file_path,
            "test_results": test_results,
        }
    else:
        return {
            "message": "No Python code found in response",
            "folder": folder_path,
            "input_file": input_file,
            "test_results": {"success": False, "error": "No test code generated"},
        }

from fastapi import FastAPI

from llm import AnthropicEngine, prompts
from services.test_generator import (
    create_pipeline_folder,
    run_test_file,
    save_input_code,
    write_test_python_file,
)

from .types import MessageRequest

UnitTestAgent = AnthropicEngine(system=prompts.unit_test_generator)

app = FastAPI()


@app.post("/generate_test_file")
def generate_test_file(request: MessageRequest):
    folder_path = create_pipeline_folder()

    input_file = save_input_code(request.content, folder_path)

    agent_response = UnitTestAgent.send_message(request.content)

    if isinstance(agent_response, list) and len(agent_response) > 0:
        text_content = agent_response[0].text
    else:
        text_content = str(agent_response)

    test_file_path = write_test_python_file(text_content, folder_path)

    if test_file_path:
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

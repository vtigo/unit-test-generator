from fastapi import FastAPI

from llm import AnthropicEngine, prompts
from utils.file import write_test_python_file

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
    response = UnitTestAgent.send_message(request.content)

    if isinstance(response, list) and len(response) > 0:
        text_content = response[0].text
    else:
        text_content = str(response)

    result = write_test_python_file(text_content)
    return {"message": result}

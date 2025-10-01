# Test Lab

Automatic unit test generator for Python and C# code using LLMs.

## Overview

Test Lab generates unit tests from source code, executes them, and produces test reports. It supports batch processing and async execution.

## Features

- Generate unit tests for Python and C# code
- Single or batch processing of code snippets
- Automatic test execution and reporting
- Async pipeline for better performance

## Requirements

- Python 3.10+
- Anthropic API key

## Installation

### Using uv (recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -e .
```

Set your API key in a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Running the examples

With uv:
```bash
uv run python main.py
```

With pip:
```bash
python main.py
```

### Python Example

```python
from pathlib import Path
from adapters import PythonAdapter
from llm.engines import AnthropicEngine
from llm.prompts import python_unit_test_generator

input_code = """def add(a, b):
    return a + b"""

llm = AnthropicEngine(system=python_unit_test_generator, max_tokens=2048)
app = PythonAdapter(input_code=input_code, work_dir=Path("storage"), llm_engine=llm)
app.run_pipeline()
```

### C# Example

```python
from adapters import CsAdapter
from llm.prompts import cs_unit_test_generator

input_code = """public class Calculator
{
    public int Add(int a, int b) { return a + b; }
}"""

llm = AnthropicEngine(system=cs_unit_test_generator, max_tokens=2048)
app = CsAdapter(input_code=input_code, work_dir=Path("storage"), llm_engine=llm)
app.run_pipeline()
```

### Batch Processing

Pass a list of code snippets to process multiple files:

```python
input_codes = [code1, code2, code3]
app = PythonAdapter(input_code=input_codes, work_dir=Path("storage"), llm_engine=llm)
app.run_pipeline()
```

## Output

Generated projects are saved in the `storage/` directory:

- `app/` - Source code files
- `tests/` - Generated test files
- `test_report.xml` - Test execution results
- `pipeline.log` - Execution logs

## Interactive Notebook

See [test_lab.ipynb](test_lab.ipynb) for interactive examples.

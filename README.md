# Test Lab

Automatic unit test generator for Python and C# code using LLMs.

## Overview

Test Lab generates unit tests from source code, executes them, and produces test reports. It uses a adapter pattern to support multiple languages with batch processing and async execution.

## Architecture

- **LanguageAdapter**: Abstract base class for language-specific operations
- **PipelineExecutor**: Orchestrates the test generation pipeline
- **Adapters**: Language-specific implementations (Python, C#)
- **LLM Engine**: Handles communication with the LLM

## Features

- Generate unit tests for Python and C# code
- Single or batch processing of code snippets
- Automatic test execution and reporting

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
from executors import PipelineExecutor
from llm.engines import AnthropicEngine
from llm.prompts import python_unit_test_generator

input_code = """def add(a, b):
    return a + b

def div(a, b):
    if b == 0:
        raise ZeroDivisionError('division by zero')
    return a / b"""

llm = AnthropicEngine(system=python_unit_test_generator, max_tokens=2048)
adapter = PythonAdapter(llm_engine=llm)

pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
pipeline.execute(input_code)
```

### C# Example

```python
from pathlib import Path
from adapters import CsAdapter
from executors import PipelineExecutor
from llm.engines import AnthropicEngine
from llm.prompts import cs_unit_test_generator

input_code = """public class Calculator
{
    public int Add(int a, int b)
    {
        return a + b;
    }

    public double Divide(double a, double b)
    {
        if (b == 0)
            throw new ArgumentException("Cannot divide by zero.");
        return a / b;
    }
}"""

llm = AnthropicEngine(system=cs_unit_test_generator, max_tokens=2048)
adapter = CsAdapter(llm_engine=llm)

pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
pipeline.execute(input_code)
```

### Batch Processing

Pass a list of code snippets to process multiple files asynchronously:

```python
input_code = [
    """def multiply(a, b):
    return a * b""",
    """def subtract(a, b):
    return a - b""",
    """def is_even(n):
    return n % 2 == 0"""
]

llm = AnthropicEngine(system=python_unit_test_generator, max_tokens=2048)
adapter = PythonAdapter(llm_engine=llm)

pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
pipeline.execute(input_code)
```

## Output

Generated projects are saved in the `storage/` directory with timestamped folder names:

**Python projects:**

- `storage/project_YYYYMMDD_HHMMSS/`
  - `app/` - Source code files (main.py or module\_\*.py)
  - `tests/` - Generated test files (test*main.py or test_module*\*.py)
  - `test_report.xml` - Test execution results

**C# projects:**

- `storage/cs_project_YYYYMMDD_HHMMSS/`
  - `src/` - Source code files (Program.cs or Module\_\*.cs) + App.csproj
  - `tests/` - Generated test files (UnitTests.cs or Module\_\*Tests.cs) + Tests.csproj
  - `test_report.xml` - Test execution results

## How It Works

1. **Initialization**: `PipelineExecutor` receives a `LanguageAdapter`, input code, and working directory
2. **Project Setup**: Adapter creates project structure (directories, config files)
3. **Code Preparation**: Adapter prepares app code (adds imports, namespaces)
4. **Test Generation**: Adapter sends code to LLM and extracts test code
5. **Test Preparation**: Adapter prepares test code (adjusts imports)
6. **File Writing**: Executor writes all files (app code, test code)
7. **Execution**: Adapter runs tests (pytest for Python, dotnet test for C#)
8. **Reporting**: Adapter generates XML report, executor writes it

## Interactive Notebook

See [test_lab.ipynb](test_lab.ipynb) for interactive examples.

## Extending

### Adding a New Language

To add support for a new language:

1. Create a new adapter inheriting from `LanguageAdapter`
2. Implement abstract methods:
   - `init_project()` - Create project structure
   - `_generate_single_test()` - Generate test code via LLM
   - `prepare_app_code()` - Prepare app code and return (code, filename)
   - `prepare_test_code()` - Prepare test code and return (code, filename)
   - `execute_tests()` - Run tests and return results
   - `generate_report()` - Generate XML report string
3. Use with `PipelineExecutor`

### Adding a New LLM Engine

To use a different LLM provider (OpenAI, Google, etc.):

1. Create a new engine class inheriting from `LLMEngine` in `llm/engines.py`
2. Implement the `send_message(content: str)` method to call your LLM API
3. Ensure the response format is compatible with existing adapters (list with `.text` or string)
4. Use with any language adapter

### Customizing Prompts

To customize test generation prompts:

1. Create a new prompt in `llm/prompts.py` or modify existing ones
2. Follow the existing format with clear instructions for the LLM
3. Specify the expected output format (code blocks, structure)
4. Pass the custom prompt when initializing the LLM engine
5. Test with your language adapter to ensure correct test generation

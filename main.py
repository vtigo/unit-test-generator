from pathlib import Path

from adapters import CsAdapter, PythonAdapter
from executors.pipeline_executor import PipelineExecutor
from llm.engines import AnthropicEngine
from llm.prompts import cs_unit_test_generator, python_unit_test_generator


def main():
    # print("=" * 50)
    # print("Testing Python with single string")
    # print("=" * 50)
    # run_python_pipeline()

    print("\n" + "=" * 50)
    print("Testing Python with list of strings (async)")
    print("=" * 50)
    run_python_pipeline_batch()

    # print("\n" + "=" * 50)
    # print("Testing C# with single string")
    # print("=" * 50)
    # run_cs_pipeline()

    # print("\n" + "=" * 50)
    # print("Testing C# with list of strings (async)")
    # print("=" * 50)
    # run_cs_pipeline_batch()


def run_python_pipeline():
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


def run_python_pipeline_batch():
    input_code = [
        """def multiply(a, b):
    return a * b

def power(a, b):
    return a ** b""",
        """def subtract(a, b):
    return a - b

def modulo(a, b):
    if b == 0:
        raise ValueError('modulo by zero')
    return a % b""",
        """def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0""",
    ]

    llm = AnthropicEngine(system=python_unit_test_generator, max_tokens=2048)
    adapter = PythonAdapter(llm_engine=llm)
    pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
    pipeline.execute(input_code)


def run_cs_pipeline():
    input_code = """public class Calculator
{
    public int Add(int a, int b)
    {
        return a + b;
    }

    public int Subtract(int a, int b)
    {
        return a - b;
    }

    public int Multiply(int a, int b)
    {
        return a * b;
    }

    public double Divide(double a, double b)
    {
        if (b == 0)
        {
            throw new ArgumentException("Cannot divide by zero.");
        }
        return a / b;
    }
}"""

    llm = AnthropicEngine(system=cs_unit_test_generator, max_tokens=2048)
    adapter = CsAdapter(llm_engine=llm)
    pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
    pipeline.execute(input_code)


def run_cs_pipeline_batch():
    input_codes = [
        """public class StringHelper
{
    public string ToUpper(string text)
    {
        return text.ToUpper();
    }

    public string Reverse(string text)
    {
        char[] array = text.ToCharArray();
        Array.Reverse(array);
        return new string(array);
    }
}""",
        """public class MathHelper
{
    public int Max(int a, int b)
    {
        return a > b ? a : b;
    }

    public int Min(int a, int b)
    {
        return a < b ? a : b;
    }
}""",
        """public class Validator
{
    public bool IsPositive(int n)
    {
        return n > 0;
    }

    public bool IsNegative(int n)
    {
        return n < 0;
    }
}""",
    ]

    llm = AnthropicEngine(system=cs_unit_test_generator, max_tokens=2048)
    adapter = CsAdapter(llm_engine=llm)
    pipeline = PipelineExecutor(language_adapter=adapter, work_dir=Path("storage"))
    pipeline.execute(input_codes)


if __name__ == "__main__":
    main()

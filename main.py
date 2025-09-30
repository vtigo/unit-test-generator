from pathlib import Path

from adapters import CsAdapter, PythonAdapter


def main():
    run_cs_pipeline()
    # run_python_pipeline()


def run_python_pipeline():
    input_code = """def add(a, b):
        return a + b

    def div(a, b):
        if b == 0:
            raise ZeroDivisionError('division by zero')
        return a / b"""

    app = PythonAdapter(input_code=input_code, work_dir=Path("storage"))
    app.run()


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

    app = CsAdapter(input_code=input_code, work_dir=Path("storage"))
    app.run()


if __name__ == "__main__":
    main()

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import LanguageAdapter


class PythonAdapter(LanguageAdapter):
    """Adapter para projetos Python."""

    language = "python"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_path: Path | None = None
        self.app_path: Path | None = None
        self.tests_path: Path | None = None

    def init_project(self, work_dir: Path) -> dict[str, Path]:
        """Cria estrutura do projeto Python com diretórios app e tests."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"project_{timestamp}"

        # cria os diretórios
        self.project_path = work_dir / project_name
        self.project_path.mkdir(parents=True, exist_ok=True)

        self.app_path = self.project_path / "app"
        self.app_path.mkdir(exist_ok=True)

        self.tests_path = self.project_path / "tests"
        self.tests_path.mkdir(exist_ok=True)

        return {
            "project_path": self.project_path,
            "app_path": self.app_path,
            "tests_path": self.tests_path,
        }

    def _generate_single_test(self, code: str) -> str:
        """Gera teste Python usando LLM e retorna o código como string."""
        response = self.llm.send_message(content=code)

        # busca o conteúdo de texto na resposta
        if isinstance(response, list) and len(response) > 0:
            text_content = response[0].text
        else:
            text_content = str(response)

        # extrai o código
        code_match = re.search(r"```python\n(.*?)\n```", text_content, re.DOTALL)
        if code_match:
            test_code = code_match.group(1)
        else:
            test_code = text_content

        return test_code

    def prepare_app_code(self, code: str, index: int) -> tuple[str, str]:
        """Prepara código Python de app e retorna (código, nome_arquivo)."""
        filename = f"module_{index}.py" if index > 0 else "main.py"
        return code, filename

    def prepare_test_code(self, test_code: str, index: int) -> tuple[str, str]:
        """Prepara código de teste Python e retorna (código_preparado, nome_arquivo)."""
        module_name = f"module_{index}" if index > 0 else "main"
        filename = f"test_module_{index}.py" if index > 0 else "test_main.py"

        # ajusta imports
        test_code = test_code.replace(
            "from main import", f"from app.{module_name} import"
        )

        return test_code, filename

    def execute_tests(self) -> dict[str, Any]:
        """Executa testes Python com pytest e retorna resultados."""
        if not self.project_path:
            raise RuntimeError("Project not initialized. Call init_project first.")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--disable-warnings",
            "--maxfail=1",
        ]

        process = subprocess.run(
            cmd,
            cwd=str(self.project_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        rc = process.returncode
        stdout = process.stdout

        return {"return_code": rc, "stdout": stdout}

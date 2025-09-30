import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import LanguageAdapter
from llm.engines import AnthropicEngine
from llm.prompts import python_unit_test_generator


class PythonAdapter(LanguageAdapter):
    """Adapter para projetos Python."""

    def init_project(self) -> str:
        """Cria estrutura do projeto Python com diretórios app e tests."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"project_{timestamp}"

        # cria os diretórios
        project_path: Path = self.work_dir / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        app_path: Path = project_path / "app"
        app_path.mkdir(exist_ok=True)

        tests_path: Path = project_path / "tests"
        tests_path.mkdir(exist_ok=True)

        # grava o código de input
        if isinstance(self.input_code, list):
            for i, code in enumerate(self.input_code):
                file_path = app_path / f"module_{i}.py"
                with open(file_path, "w") as f:
                    f.write(code)
        else:
            main_file_path = app_path / "main.py"
            with open(main_file_path, "w") as f:
                f.write(self.input_code)

        # configura logging
        log_path = project_path / "pipeline.log"
        self.logger = logging.getLogger(project_name)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(handler)

        self.logger.info(f"Project initialized at {project_path}")

        self.project_path = project_path
        self.tests_path = tests_path
        self.app_path = app_path

        return str(project_path)

    def _generate_single_test(self, code: str, index: int) -> str:
        """Gera arquivo de teste Python usando LLM e retorna o caminho."""
        # determina o nome do arquivo
        if isinstance(self.input_code, list):
            test_filename = f"test_module_{index}.py"
            module_name = f"module_{index}"
        else:
            test_filename = "test_main.py"
            module_name = "main"

        llm = AnthropicEngine(system=python_unit_test_generator, max_tokens=2048)

        # envia requisição à LLM
        response = llm.send_message(content=code)
        self.logger.info("Received response from LLM")

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

        # atualiza o import do código de teste para o diretório correto
        test_code = test_code.replace(
            "from main import", f"from app.{module_name} import"
        )

        # grava o código de teste
        test_file_path: Path = self.tests_path / test_filename
        with open(test_file_path, "w") as f:
            f.write(test_code)

        self.logger.info(f"Test file generated at {test_file_path}")
        return str(test_file_path)

    def execute_tests(self) -> dict[str, Any]:
        """Executa testes Python com pytest e retorna resultados."""
        self.logger.info("Starting test execution")
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

        self.logger.info(f"Test execution completed with return code {rc}")
        return {"return_code": rc, "stdout": stdout}

    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório XML dos resultados dos testes e retorna o caminho."""
        import xml.etree.ElementTree as ET

        root = ET.Element("test_report")
        ET.SubElement(root, "timestamp").text = datetime.now().isoformat()
        ET.SubElement(root, "project_path").text = str(self.project_path)
        ET.SubElement(root, "return_code").text = str(test_results["return_code"])
        ET.SubElement(root, "output").text = test_results["stdout"]
        ET.SubElement(root, "status").text = (
            "passed" if test_results["return_code"] == 0 else "failed"
        )

        tree = ET.ElementTree(root)
        report_path: Path = self.project_path / "test_report.xml"
        tree.write(report_path, encoding="utf-8", xml_declaration=True)

        self.logger.info(f"Report generated at {report_path}")
        return str(report_path)

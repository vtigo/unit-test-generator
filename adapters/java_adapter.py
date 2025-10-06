import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import LanguageAdapter


class JavaAdapter(LanguageAdapter):
    """Adapter para projetos Java."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_path: Path | None = None
        self.app_path: Path | None = None
        self.tests_path: Path | None = None

    def init_project(self, work_dir: Path) -> dict[str, Path]:
        """Cria estrutura do projeto com diretórios src e tests."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"java_project_{timestamp}"

        # cria os diretórios
        self.project_path = work_dir / project_name
        self.project_path.mkdir(parents=True, exist_ok=True)

        self.app_path = self.project_path / "src"
        self.app_path.mkdir(exist_ok=True)

        self.tests_path = self.project_path / "tests"
        self.tests_path.mkdir(exist_ok=True)

        return {
            "project_path": self.project_path,
            "app_path": self.app_path,
            "tests_path": self.tests_path,
        }

    def _generate_single_test(self, code: str) -> str:
        """Gera teste usando LLM e retorna o código como string."""
        # envia requisição à LLM injetado
        response = self.llm.send_message(content=code)

        # busca o conteúdo de texto na resposta
        if isinstance(response, list) and len(response) > 0:
            text_content = response[0].text
        else:
            text_content = str(response)

        # extrai o código Java (tenta diferentes formatos de markdown)
        code_match = re.search(
            r"```(?:java)\n(.*?)\n```", text_content, re.DOTALL | re.IGNORECASE
        )
        if code_match:
            test_code = code_match.group(1)
        else:
            # tenta capturar blocos genéricos de código se não encontrou Java específico
            generic_match = re.search(r"```\n(.*?)\n```", text_content, re.DOTALL)
            if generic_match:
                test_code = generic_match.group(1)
            else:
                test_code = text_content

        return test_code

    def prepare_app_code(self, code: str, index: int) -> tuple[str, str]:
        """Prepara código de app e retorna (código_preparado, nome_arquivo)."""
        # extrai o nome da classe pública do código
        import re

        class_match = re.search(r"public\s+class\s+(\w+)", code)
        if class_match:
            class_name = class_match.group(1)
            filename = f"{class_name}.java"
        else:
            # fallback se não encontrar uma classe pública
            filename = f"Module{index}.java" if index > 0 else "Main.java"

        return code, filename

    def prepare_test_code(self, test_code: str, index: int) -> tuple[str, str]:
        """Prepara código de teste e retorna (código, nome_arquivo)."""
        # extrai o nome da classe de teste do código
        import re

        class_match = re.search(r"public\s+class\s+(\w+)", test_code)
        if class_match:
            class_name = class_match.group(1)
            filename = f"{class_name}.java"
        else:
            # fallback se não encontrar uma classe pública
            filename = f"Module{index}Test.java" if index > 0 else "MainTest.java"

        return test_code, filename

    def execute_tests(self) -> dict[str, Any]:
        """Executa testes e retorna resultados."""
        if not self.tests_path or not self.app_path or not self.project_path:
            raise RuntimeError("Project not initialized. Call init_project first.")

        # cria diretório para classes compiladas
        bin_path = self.project_path / "bin"
        bin_path.mkdir(exist_ok=True)

        # compila código fonte
        src_files = list(self.app_path.glob("*.java"))
        if not src_files:
            return {
                "return_code": 1,
                "stdout": "No source files found in src directory",
            }

        # converte para caminhos relativos ao diretório do projeto
        relative_src_files = [str(f.relative_to(self.project_path)) for f in src_files]

        compile_cmd = ["javac", "-d", "bin"] + relative_src_files
        compile_process = subprocess.run(
            compile_cmd,
            cwd=str(self.project_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if compile_process.returncode != 0:
            return {
                "return_code": compile_process.returncode,
                "stdout": f"Compilation failed:\n{compile_process.stdout}",
            }

        # compila testes (sem dependências externas)
        test_files = list(self.tests_path.glob("*.java"))
        if test_files:
            # converte para caminhos relativos ao diretório do projeto
            relative_test_files = [
                str(f.relative_to(self.project_path)) for f in test_files
            ]

            # compila os testes com as classes de app no classpath
            compile_test_cmd = [
                "javac",
                "-cp",
                "bin",
                "-d",
                "bin",
            ] + relative_test_files

            compile_test_process = subprocess.run(
                compile_test_cmd,
                cwd=str(self.project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            if compile_test_process.returncode != 0:
                return {
                    "return_code": compile_test_process.returncode,
                    "stdout": f"Test compilation failed:\n{compile_test_process.stdout}",
                }

            # executa cada classe de teste (cada uma tem um main)
            test_classes = [f.stem for f in test_files]
            all_output = []

            for test_class in test_classes:
                run_test_cmd = [
                    "java",
                    "-cp",
                    "bin",
                    test_class,
                ]

                run_test_process = subprocess.run(
                    run_test_cmd,
                    cwd=str(self.project_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )

                all_output.append(run_test_process.stdout)

                if run_test_process.returncode != 0:
                    return {
                        "return_code": run_test_process.returncode,
                        "stdout": "\n".join(all_output),
                    }

            return {"return_code": 0, "stdout": "\n".join(all_output)}

        return {"return_code": 0, "stdout": "No tests found"}

    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório XML dos resultados dos testes e retorna como string."""
        import xml.etree.ElementTree as ET

        if not self.project_path:
            raise RuntimeError("Project not initialized. Call init_project first.")

        root = ET.Element("test_report")
        ET.SubElement(root, "timestamp").text = datetime.now().isoformat()
        ET.SubElement(root, "project_path").text = str(self.project_path)
        ET.SubElement(root, "language").text = "java"
        ET.SubElement(root, "return_code").text = str(test_results["return_code"])
        ET.SubElement(root, "output").text = test_results["stdout"]
        ET.SubElement(root, "status").text = (
            "passed" if test_results["return_code"] == 0 else "failed"
        )

        return ET.tostring(root, encoding="unicode", xml_declaration=False)

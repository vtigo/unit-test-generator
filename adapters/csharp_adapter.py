import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import LanguageAdapter
from llm.engines import AnthropicEngine
from llm.prompts import cs_unit_test_generator


class CsAdapter(LanguageAdapter):
    """Adapter para projetos C#."""

    def init_project(self) -> str:
        """Cria estrutura do projeto C# com arquivos .csproj e diretórios src e tests."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"cs_project_{timestamp}"

        # cria os diretórios
        project_path: Path = self.work_dir / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        app_path: Path = project_path / "src"
        app_path.mkdir(exist_ok=True)

        tests_path: Path = project_path / "tests"
        tests_path.mkdir(exist_ok=True)

        # cria arquivo de projeto .csproj para a aplicação
        app_csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>"""

        with open(app_path / "App.csproj", "w") as f:
            f.write(app_csproj_content)

        # cria arquivo de projeto .csproj para os testes
        test_csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.6.0" />
    <PackageReference Include="xunit" Version="2.4.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.3">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="../src/App.csproj" />
  </ItemGroup>
</Project>"""

        with open(tests_path / "Tests.csproj", "w") as f:
            f.write(test_csproj_content)

        # grava o código de input com using directives necessárias
        def add_using_directives(code: str) -> str:
            if "using System;" not in code:
                # adiciona using System; no início se não existir
                if not code.strip().startswith("using"):
                    return "using System;\n\n" + code
                else:
                    # se já tem outras using directives, adiciona System se necessário
                    lines = code.split("\n")
                    using_lines = []
                    other_lines = []
                    found_system = False

                    for line in lines:
                        if line.strip().startswith("using "):
                            using_lines.append(line)
                            if "using System;" in line:
                                found_system = True
                        else:
                            other_lines.append(line)

                    if not found_system:
                        using_lines.insert(0, "using System;")

                    return "\n".join(using_lines + [""] + other_lines)
            return code

        if isinstance(self.input_code, list):
            for i, code in enumerate(self.input_code):
                file_path = app_path / f"Module_{i}.cs"
                code_to_write = add_using_directives(code)
                with open(file_path, "w") as f:
                    f.write(code_to_write)
        else:
            main_file_path = app_path / "Program.cs"
            code_to_write = add_using_directives(self.input_code)
            with open(main_file_path, "w") as f:
                f.write(code_to_write)

        # configura logging
        log_path = project_path / "pipeline.log"
        self.logger = logging.getLogger(project_name)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(handler)

        self.logger.info(f"C# project initialized at {project_path}")

        self.project_path = project_path
        self.tests_path = tests_path
        self.app_path = app_path

        return str(project_path)

    def _generate_single_test(self, code: str, index: int) -> str:
        """Gera arquivo de teste C# usando LLM e retorna o caminho."""
        # determina o nome do arquivo
        if isinstance(self.input_code, list):
            test_filename = f"Module_{index}Tests.cs"
        else:
            test_filename = "UnitTests.cs"

        llm = AnthropicEngine(system=cs_unit_test_generator, max_tokens=2048)

        # envia requisição à LLM
        response = llm.send_message(content=code)
        self.logger.info("Received response from LLM")

        # busca o conteúdo de texto na resposta
        if isinstance(response, list) and len(response) > 0:
            text_content = response[0].text
        else:
            text_content = str(response)

        # extrai o código C# (tenta diferentes formatos de markdown)
        code_match = re.search(
            r"```(?:csharp|cs|c#)\n(.*?)\n```", text_content, re.DOTALL | re.IGNORECASE
        )
        if code_match:
            test_code = code_match.group(1)
        else:
            # tenta capturar blocos genéricos de código se não encontrou C# específico
            generic_match = re.search(r"```\n(.*?)\n```", text_content, re.DOTALL)
            if generic_match:
                test_code = generic_match.group(1)
            else:
                test_code = text_content

        # grava o código de teste
        test_file_path: Path = self.tests_path / test_filename
        with open(test_file_path, "w") as f:
            f.write(test_code)

        self.logger.info(f"C# test file generated at {test_file_path}")
        return str(test_file_path)

    def execute_tests(self) -> dict[str, Any]:
        """Executa testes C# com dotnet test e retorna resultados."""
        self.logger.info("Starting C# test execution")

        # primeiro, restaura as dependências
        restore_cmd = ["dotnet", "restore"]
        restore_process = subprocess.run(
            restore_cmd,
            cwd=str(self.tests_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if restore_process.returncode != 0:
            self.logger.error(f"Failed to restore packages: {restore_process.stdout}")
            return {
                "return_code": restore_process.returncode,
                "stdout": restore_process.stdout,
            }

        # executa os testes
        test_cmd = ["dotnet", "test", "--verbosity", "minimal", "--no-restore"]
        test_process = subprocess.run(
            test_cmd,
            cwd=str(self.tests_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        rc = test_process.returncode
        stdout = test_process.stdout

        self.logger.info(f"C# test execution completed with return code {rc}")
        return {"return_code": rc, "stdout": stdout}

    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório XML dos resultados dos testes C# e retorna o caminho."""
        import xml.etree.ElementTree as ET

        root = ET.Element("test_report")
        ET.SubElement(root, "timestamp").text = datetime.now().isoformat()
        ET.SubElement(root, "project_path").text = str(self.project_path)
        ET.SubElement(root, "language").text = "csharp"
        ET.SubElement(root, "return_code").text = str(test_results["return_code"])
        ET.SubElement(root, "output").text = test_results["stdout"]
        ET.SubElement(root, "status").text = (
            "passed" if test_results["return_code"] == 0 else "failed"
        )

        tree = ET.ElementTree(root)
        report_path: Path = self.project_path / "test_report.xml"
        tree.write(report_path, encoding="utf-8", xml_declaration=True)

        self.logger.info(f"C# report generated at {report_path}")
        return str(report_path)

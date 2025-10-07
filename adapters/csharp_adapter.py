import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import LanguageAdapter


class CsAdapter(LanguageAdapter):
    """Adapter para projetos C#."""

    language = "csharp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_path: Path | None = None
        self.source_path: Path | None = None
        self.tests_path: Path | None = None

    def init_project(self, work_dir: Path) -> dict[str, Path]:
        """Cria estrutura do projeto C# com arquivos .csproj e diretórios src e tests."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"cs_project_{timestamp}"

        # cria os diretórios
        self.project_path = work_dir / project_name
        self.project_path.mkdir(parents=True, exist_ok=True)

        self.source_path = self.project_path / "src"
        self.source_path.mkdir(exist_ok=True)

        self.tests_path = self.project_path / "tests"
        self.tests_path.mkdir(exist_ok=True)

        # cria arquivo de projeto .csproj para a aplicação
        app_csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>"""

        with open(self.source_path / "App.csproj", "w") as f:
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

        with open(self.tests_path / "Tests.csproj", "w") as f:
            f.write(test_csproj_content)

        return {
            "project_path": self.project_path,
            "source_path": self.source_path,
            "tests_path": self.tests_path,
        }

    def _generate_single_test(self, code: str) -> str:
        """Gera teste C# usando LLM e retorna o código como string."""
        # envia requisição à LLM injetado
        response = self.llm.send_message(content=code)

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

        return test_code

    def prepare_source_code(self, code: str, index: int) -> tuple[str, str]:
        """Prepara código e retorna (código_preparado, nome_arquivo)."""
        filename = f"Module_{index}.cs" if index > 0 else "Program.cs"

        # adiciona using System se necessário
        if "using System;" not in code:
            if not code.strip().startswith("using"):
                code = "using System;\n\n" + code

        return code, filename

    def prepare_test_code(self, test_code: str, index: int) -> tuple[str, str]:
        """Prepara código de teste C# e retorna (código, nome_arquivo)."""
        filename = f"Module_{index}Tests.cs" if index > 0 else "UnitTests.cs"
        return test_code, filename

    def execute_tests(self) -> dict[str, Any]:
        """Executa testes C# com dotnet test e retorna resultados."""
        if not self.tests_path:
            raise RuntimeError("Project not initialized. Call init_project first.")

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

        return {"return_code": rc, "stdout": stdout}

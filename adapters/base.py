import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class LanguageAdapter(ABC):
    """Classe base para adapters de linguagens de programação."""

    def __init__(self, input_code: str | list[str], work_dir: Path):
        """Inicializa o adapter com código de entrada e diretório de trabalho."""
        self.input_code = input_code
        self.work_dir = work_dir
        self.logger = None

    @abstractmethod
    def init_project(self) -> str:
        """Inicializa estrutura do projeto e retorna o caminho."""
        pass

    @abstractmethod
    def execute_tests(self) -> dict[str, Any]:
        """Executa os testes e retorna os resultados."""
        pass

    @abstractmethod
    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório dos resultados dos testes e retorna o caminho."""
        pass

    @abstractmethod
    def _generate_single_test(self, code: str, index: int) -> str:
        """Gera um arquivo de teste para o código fornecido e retorna o caminho."""
        pass

    async def _process_test_generation_batch(self) -> list[str]:
        """Processa múltiplos códigos de entrada de forma assíncrona."""
        tasks = [
            asyncio.to_thread(self._generate_single_test, code, i)
            for i, code in enumerate(self.input_code)
        ]
        return await asyncio.gather(*tasks)

    def generate_tests(self) -> str | list[str]:
        """Gera testes para o código de entrada."""

        if isinstance(self.input_code, list):
            return asyncio.run(self._process_test_generation_batch())
        else:
            return self._generate_single_test(self.input_code, 0)

    def run_pipeline(self):
        """Executa o pipeline completo: inicializa projeto, gera testes, executa e gera relatório."""
        project_path = self.init_project()
        print(f"Projeto gerado em {project_path}")

        tests_path = self.generate_tests()
        if isinstance(tests_path, list):
            for path in tests_path:
                print(f"Arquivo de teste gerado em {path}")
        else:
            print(f"Arquivo de teste gerado em {tests_path}")

        test_results = self.execute_tests()

        report_path = self.generate_report(test_results)
        print(f"Arquivo de relatório gerado em {report_path}")

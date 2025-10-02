import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from llm.engines import LLMEngine


class LanguageAdapter(ABC):
    """Classe base para adapters de linguagens de programação."""

    def __init__(
        self,
        llm_engine: LLMEngine,
    ):
        self.llm = llm_engine

    @abstractmethod
    def init_project(self, work_dir: Path) -> dict[str, Path]:
        """Inicializa estrutura do projeto e retorna os caminhos."""
        pass

    @abstractmethod
    def execute_tests(self) -> dict[str, Any]:
        """Executa os testes e retorna os resultados."""
        pass

    @abstractmethod
    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório dos resultados dos testes e retorna como string."""
        pass

    @abstractmethod
    def _generate_single_test(self, code: str, index: int) -> str:
        """Gera um teste unitário para o código fornecido e retorna como string."""
        pass

    @abstractmethod
    def prepare_app_code(self, code: str, index: int) -> tuple[str, str]:
        """Prepara código de app e retorna (código_preparado, nome_arquivo)."""
        pass

    @abstractmethod
    def prepare_test_code(self, test_code: str, index: int) -> tuple[str, str]:
        """Prepara código de teste e retorna (código_preparado, nome_arquivo)."""
        pass

    async def _process_test_generation_batch(
        self, input_code: str | list[str]
    ) -> list[str]:
        """Processa múltiplos códigos de entrada de forma assíncrona."""
        tasks = [
            asyncio.to_thread(self._generate_single_test, code, i)
            for i, code in enumerate(input_code)
        ]
        return await asyncio.gather(*tasks)

    def generate_tests(self, input_code: str | list[str]) -> str | list[str]:
        """Gera testes para o código de entrada."""

        if isinstance(input_code, list):
            return asyncio.run(self._process_test_generation_batch(input_code))
        else:
            return self._generate_single_test(input_code, 0)

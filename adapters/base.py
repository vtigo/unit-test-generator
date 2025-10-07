import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from llm.engines import LLMEngine


class LanguageAdapter(ABC):
    """Classe base para adapters de linguagens de programação."""

    language: str  # Deve ser definido nas subclasses

    def __init__(
        self,
        llm_engine: LLMEngine,
    ):
        self.llm = llm_engine
        self.project_path: Path | None = None

    @abstractmethod
    def init_project(self, work_dir: Path) -> dict[str, Path]:
        """Inicializa estrutura do projeto e retorna os caminhos."""
        pass

    @abstractmethod
    def execute_tests(self) -> dict[str, Any]:
        """Executa os testes e retorna os resultados."""
        pass

    @abstractmethod
    def _generate_single_test(self, code: str) -> str:
        """Gera um teste unitário para o código fornecido e retorna como string."""
        pass

    @abstractmethod
    def prepare_source_code(self, code: str, index: int) -> tuple[str, str]:
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
            asyncio.to_thread(self._generate_single_test, code) for code in input_code
        ]
        return await asyncio.gather(*tasks)

    def generate_tests(self, input_code: str | list[str]) -> str | list[str]:
        """Gera testes para o código de entrada."""

        if isinstance(input_code, list):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # No event loop running, use asyncio.run()
                return asyncio.run(self._process_test_generation_batch(input_code))
            else:
                # Event loop already running (e.g., in Jupyter), use nest_asyncio
                import nest_asyncio

                nest_asyncio.apply()
                return asyncio.run(self._process_test_generation_batch(input_code))
        else:
            return self._generate_single_test(input_code)

    def generate_report(self, test_results: dict[str, Any]) -> str:
        """Gera relatório XML dos resultados dos testes e retorna como string."""
        import xml.etree.ElementTree as ET

        if not self.project_path:
            raise RuntimeError("Project not initialized. Call init_project first.")

        root = ET.Element("test_report")
        ET.SubElement(root, "timestamp").text = datetime.now().isoformat()
        ET.SubElement(root, "project_path").text = str(self.project_path)
        ET.SubElement(root, "language").text = self.language
        ET.SubElement(root, "return_code").text = str(test_results["return_code"])
        ET.SubElement(root, "output").text = test_results["stdout"]
        ET.SubElement(root, "status").text = (
            "passed" if test_results["return_code"] == 0 else "failed"
        )

        return ET.tostring(root, encoding="unicode", xml_declaration=False)

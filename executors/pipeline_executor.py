from pathlib import Path

from adapters.base import LanguageAdapter


class PipelineExecutor:
    def __init__(
        self,
        language_adapter: LanguageAdapter,
        work_dir: Path,
    ) -> None:
        self.adapter = language_adapter
        self.work_dir = work_dir

    def execute(self, input_code: str | list[str]):
        """Executa o pipeline completo: inicializa projeto, gera testes, executa e gera relatório."""
        # inicializa estrutura do projeto
        paths = self.adapter.init_project(self.work_dir)
        app_path = paths["app_path"]
        tests_path = paths["tests_path"]

        # grava o código de input
        codes = input_code if isinstance(input_code, list) else [input_code]
        for i, code in enumerate(codes):
            prepared_code, filename = self.adapter.prepare_app_code(code, i)
            with open(app_path / filename, "w") as f:
                f.write(prepared_code)

        # gera os testes (retorna strings de código)
        test_codes = self.adapter.generate_tests(input_code)

        # grava os arquivos de teste
        test_codes_list = test_codes if isinstance(test_codes, list) else [test_codes]
        for i, test_code in enumerate(test_codes_list):
            prepared_test, filename = self.adapter.prepare_test_code(test_code, i)
            test_file_path = tests_path / filename
            with open(test_file_path, "w") as f:
                f.write(prepared_test)
            print(f"Arquivo de teste gerado em {test_file_path}")

        # executa os testes
        test_results = self.adapter.execute_tests()

        # gera o relatório (retorna string XML)
        report_xml = self.adapter.generate_report(test_results)

        # grava o arquivo de relatório
        report_path = paths["project_path"] / "test_report.xml"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(report_xml)
        print(f"Arquivo de relatório gerado em {report_path}")

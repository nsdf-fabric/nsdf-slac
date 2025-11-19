import os
import pytest
from typer.testing import CliRunner
from nsdf_dark_matter_cli.cli import app
from typing import Dict

runner = CliRunner()


@pytest.fixture
def golden_files() -> Dict[str, str]:
    return {
        "limit": os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "ls_lim_golden.txt")),
        "prefix": os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "ls_prefix_golden.txt")),
        "all": os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "ls_all_parameters_golden.txt"))
    }


class TestListCommand:
    def _compare_with_golden(self, result_bytes: bytes, golden_path: str):
        with open(golden_path, "rb") as f:
            golden_bytes = f.read()
        assert result_bytes == golden_bytes, f"Output differs from {golden_path}"

    def test_ls_limit(self, golden_files: Dict[str, str]):
        """Compare ls command with --limit against golden file"""
        result = runner.invoke(app, ["ls", "--limit", "5"])

        assert result.exit_code == 0

        result_bytes = result.stdout_bytes
        self._compare_with_golden(result_bytes, golden_files["limit"])

    def test_ls_prefix(self, golden_files: Dict[str, str]):
        """Compare ls command with --prefix against golden file"""
        result = runner.invoke(app, ["ls", "--prefix", "07220702_1055"])

        assert result.exit_code == 0

        result_bytes = result.stdout_bytes
        self._compare_with_golden(result_bytes, golden_files["prefix"])

    def test_all_parameters(self, golden_files: Dict[str, str]):
        """Compare ls command with --prefix against golden file"""
        result = runner.invoke(app, ["ls", "--prefix", "072", "--limit", "10"])

        assert result.exit_code == 0

        result_bytes = result.stdout_bytes
        self._compare_with_golden(result_bytes, golden_files["all"])

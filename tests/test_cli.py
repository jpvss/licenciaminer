"""Testes para a interface CLI."""

from click.testing import CliRunner

from licenciaminer.cli import cli


class TestCli:
    """Testes para os comandos CLI."""

    def test_help(self) -> None:
        """Deve mostrar ajuda."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LicenciaMiner" in result.output

    def test_collect_help(self) -> None:
        """Deve mostrar ajuda do subcomando collect."""
        runner = CliRunner()
        result = runner.invoke(cli, ["collect", "--help"])
        assert result.exit_code == 0
        assert "ibama" in result.output
        assert "anm" in result.output
        assert "mg" in result.output

    def test_analyze_help(self) -> None:
        """Deve mostrar ajuda do subcomando analyze."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "output" in result.output.lower()

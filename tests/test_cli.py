from unittest.mock import patch

from mark2tex.cli import build_parser


def test_parser_creates_successfully():
    parser = build_parser()
    assert parser is not None

def test_parser_prog_name():
    parser = build_parser()
    assert parser.prog == "mark2tex"

def test_subcommand_tui_exists():
    parser = build_parser()
    args = parser.parse_args(["tui"])
    assert args.command == "tui"

def test_subcommand_doctor_exists():
    parser = build_parser()
    args = parser.parse_args(["doctor"])
    assert args.command == "doctor"

def test_subcommand_uninstall_exists():
    parser = build_parser()
    args = parser.parse_args(["uninstall"])
    assert args.command == "uninstall"

def test_subcommand_template_list_exists():
    parser = build_parser()
    args = parser.parse_args(["template", "list"])
    assert args.command == "template"
    assert args.action == "list"

def test_default_command_is_tui():
    parser = build_parser()
    args = parser.parse_args([])
    command = args.command or "tui"
    assert command == "tui"

def test_doctor_command_calls_run_check() -> None:
    with patch("mark2tex.cli._run_check") as mock_run:
        from mark2tex.cli import main
        with patch("sys.argv", ["mark2tex", "doctor"]):
            main()
        mock_run.assert_called_once()

def test_uninstall_command_calls_uninstall_assets() -> None:
    with patch("mark2tex.cli.uninstall_docker_assets") as mock_uninstall:
        with patch("sys.argv", ["mark2tex", "uninstall"]):
            with patch("builtins.print"):  # silencia o print
                from mark2tex.cli import main
                main()
        mock_uninstall.assert_called_once()


def test_template_list_runs_without_crashing() -> None:
    # We only assert that main() runs and calls print at least once.
    with patch("builtins.print") as mock_print:
        with patch("sys.argv", ["mark2tex", "template", "list"]):
            from mark2tex.cli import main
            main()
        assert mock_print.called

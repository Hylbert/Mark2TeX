from unittest.mock import patch

from src.cli import build_parser


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

def test_default_command_is_tui():
    parser = build_parser()
    args = parser.parse_args([])
    command = args.command or "tui"
    assert command == "tui"

def test_doctor_command_calls_ensure_environment() -> None:
    with patch("src.cli.ensure_environment") as mock_env:
        from src.cli import main
        with patch("sys.argv", ["mark2tex", "doctor"]):
            main()
        mock_env.assert_called_once_with(check_only=True)

def test_uninstall_command_calls_uninstall_assets() -> None:
    with patch("src.cli.uninstall_docker_assets") as mock_uninstall:
        with patch("sys.argv", ["mark2tex", "uninstall"]):
            with patch("builtins.print"):  # silencia o print
                from src.cli import main
                main()
        mock_uninstall.assert_called_once()

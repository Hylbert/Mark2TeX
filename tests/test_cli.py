import sys
from unittest.mock import patch

from mark2tex.cli import build_parser


def test_parser_prog_name():
    parser = build_parser()
    assert parser.prog == "mark2tex"


def test_parser_has_doctor_subcommand():
    parser = build_parser()
    subparsers_actions = [
        action
        for action in parser._actions
        if hasattr(action, "_name_parser_map")
    ]
    assert any(
        "doctor" in action._name_parser_map
        for action in subparsers_actions
    )


def test_doctor_command(capsys):
    with patch("mark2tex.cli.ensure_environment") as mock_env:
        from mark2tex.cli import main
        with patch("sys.argv", ["mark2tex", "doctor"]):
            try:
                main()
            except SystemExit:
                pass
        mock_env.assert_called_once()


def test_uninstall_command(capsys):
    with patch("mark2tex.cli.uninstall_docker_assets") as mock_uninstall:
        with patch("sys.argv", ["mark2tex", "uninstall"]):
            try:
                from mark2tex.cli import main
                main()
            except SystemExit:
                pass
        mock_uninstall.assert_called_once()

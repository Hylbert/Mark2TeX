from __future__ import annotations

from .config import SUPPORTED_LANGUAGES

_STRINGS: dict[str, dict[str, str]] = {
    "pt_BR": {
        # Menu Global
        "menu.settings": "AJUSTES",
        "menu.help": "AJUDA",
        "menu.exit": "SAIR",
        # Tela de Settings
        "settings.title": "AJUSTES",
        "settings.language": "Idioma da interface",
        "settings.save": "SALVAR",
        "settings.cancel": "CANCELAR",
        "settings.saved_at": "Configurações salvas em:",
        # Console / compilação
        "compile.select_file": "❌ Selecione um arquivo e um template para compilar.",
        "compile.select_watch": "❌ Selecione um arquivo e um template antes de ativar o Watch Mode.",
        "compile.start": "🚀 Compilando",
        "compile.error": "❌ Erro inesperado",
        "watch.on": "🔭 Watch Mode ativado para",
        "watch.off": "💤 Watch Mode desativado.",
        # Border titles
        "panel.files": "• Arquivos",
        "panel.config": "• Configuração",
        "panel.preview": "• Preview",
        "panel.console": "• Console",
        "panel.template_label": "Defina o Template do Arquivo PDF",
        # Botões
        "btn.compile": "COMPILAR",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "Arquivo  : —",
        "status.template": "Template : —",
        # Help
        "help.title": "AJUDA & ATALHOS",
        "help.footer": "Pressione ESC para voltar",
    },
    "en_US": {
        # Menu Global
        "menu.settings": "SETTINGS",
        "menu.help": "HELP",
        "menu.exit": "EXIT",
        # Tela de Settings
        "settings.title": "SETTINGS",
        "settings.language": "Interface language",
        "settings.save": "SAVE",
        "settings.cancel": "CANCEL",
        "settings.saved_at": "Settings saved at:",
        # Console / compilação
        "compile.select_file": "❌ Select a file and a template to compile.",
        "compile.select_watch": "❌ Select a file and a template before enabling Watch Mode.",
        "compile.start": "🚀 Compiling",
        "compile.error": "❌ Unexpected error",
        "watch.on": "🔭 Watch Mode enabled for",
        "watch.off": "💤 Watch Mode disabled.",
        # Border titles
        "panel.files": "• Files",
        "panel.config": "• Settings",
        "panel.preview": "• Preview",
        "panel.console": "• Console",
        "panel.template_label": "Set the PDF Template",
        # Botões
        "btn.compile": "COMPILE",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "File     : —",
        "status.template": "Template : —",
        # Help
        "help.title": "HELP & SHORTCUTS",
        "help.footer": "Press ESC to go back",
    },
}

_current: str = "pt_BR"


def set_language(lang: str) -> None:
    """Define o idioma ativo. Ignorado se o idioma não for suportado."""
    global _current
    if lang in SUPPORTED_LANGUAGES:
        _current = lang


def get_language() -> str:
    """Retorna o código do idioma atual."""
    return _current


def t(key: str) -> str:
    """Traduz uma chave. Fallback para pt_BR se não encontrar."""
    return (
        _STRINGS.get(_current, {}).get(key)
        or _STRINGS["pt_BR"].get(key, key)
    )

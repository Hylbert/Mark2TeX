from __future__ import annotations

from .config import SUPPORTED_LANGUAGES

_STRINGS: dict[str, dict[str, str]] = {
    "pt_BR": {
        # Menu Global
        "menu.settings": "AJUSTES",
        "menu.help": "AJUDA",
        "menu.exit": "SAIR",
        # Abas de settings
        "settings.tab_general": "geral",
        # Opções de settings
        "settings.opt_language": "Idioma",
        "settings.desc_language": (
            "Define o idioma da interface.\n\n"
            "Use \u2190 \u2192 para alternar entre\n"
            "os idiomas dispon\u00edveis.\n\n"
            "A altera\u00e7\u00e3o \u00e9 aplicada\nimediatamente."
        ),
        "settings.saved_at": "Config em:",
        # Console / compila\u00e7\u00e3o
        "compile.select_file": "\u274c Selecione um arquivo e um template para compilar.",
        "compile.select_watch": "\u274c Selecione um arquivo e um template antes de ativar o Watch Mode.",
        "compile.start": "\U0001f680 Compilando",
        "compile.error": "\u274c Erro inesperado",
        "watch.on": "\U0001f52d Watch Mode ativado para",
        "watch.off": "\U0001f4a4 Watch Mode desativado.",
        # Border titles
        "panel.files": "\u2022 Arquivos",
        "panel.config": "\u2022 Configura\u00e7\u00e3o",
        "panel.preview": "\u2022 Preview",
        "panel.console": "\u2022 Console",
        "panel.template_label": "Defina o Template do Arquivo PDF",
        # Bot\u00f5es
        "btn.compile": "COMPILAR",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "Arquivo  : \u2014",
        "status.template": "Template : \u2014",
        # Help
        "help.title": "AJUDA & ATALHOS",
        "help.footer": "Pressione ESC para voltar",
        "help.bindings_title": "Atalhos de teclado:",
        "help.flow_title": "Fluxo de uso:",
        "help.flow_1": "1. Selecione um arquivo .md no painel esquerdo",
        "help.flow_2": "2. Escolha o template (tcc, artigo, projeto)",
        "help.flow_3": "3. Pressione c ou clique em COMPILAR",
        "help.flow_4": "4. Acompanhe o progresso no console abaixo",
        # log_translator
        "log.config_reading": "\u2699\ufe0f Config: lendo arquivos de configura\u00e7\u00e3o",
        "log.config_file": "\u2699\ufe0f Config: {path}",
        "log.output_written": "\U0001f4c4 Sa\u00edda gerada: {fmt} ({pages} p\u00e1ginas)",
        "log.applying_rule": "\U0001f527 Aplicando regra: {name}",
        "log.latexmk_version": "\u2139\ufe0f Latexmk {ver}",
        "log.refs_changed": "\U0001f504 Refer\u00eancias alteradas, recompilando...",
        "log.bib_file": "\U0001f4da Arquivo de refer\u00eancias: {fname}",
        "log.engine_xetex": "\u2139\ufe0f Motor: XeTeX {ver}",
        "log.engine_bibtex": "\u2139\ufe0f Motor: BibTeX {ver}",
        "log.doc_class": "\U0001f4c4 Classe: {cls}{ver}",
        "log.run_n": "\U0001f504 Compila\u00e7\u00e3o {n} \u2014 regra: {rule}",
        "log.running_xelatex": "\u25b6\ufe0f xelatex output.tex",
        "log.running_bibtex": "\u25b6\ufe0f bibtex {arg}",
        "log.running_cmd": "\u25b6\ufe0f {cmd}",
        "log.latex_error": "\u274c Erro LaTeX: {msg}",
        "log.error": "\u274c {msg}",
        "log.line_ref_ctx": "   \u21b3 linha {n}: {ctx}",
        "log.line_ref": "   \u21b3 linha {n}",
        "log.overfull": "\u26a0\ufe0f Texto largo ({amount}) nas linhas {l1}\u2013{l2}",
        "log.pkg_warn": "\u26a0\ufe0f [{pkg}] {msg}",
        "log.latex_warn": "\u26a0\ufe0f {msg}",
        "log.bib_style": "\U0001f4dd Estilo bibliogr\u00e1fico: {sty}",
        "log.bib_db": "\U0001f4da Base de dados: {db}",
        "log.no_citations": "\u2139\ufe0f Nenhuma cita\u00e7\u00e3o encontrada no documento",
        "log.bib_errors": "\u274c {msg}",
        "log.refs_empty": "\u26a0\ufe0f Se\u00e7\u00e3o de refer\u00eancias vazia",
        "log.latexmk_generic": "\U0001f527 Latexmk: {msg}",
    },
    "en_US": {
        # Menu Global
        "menu.settings": "SETTINGS",
        "menu.help": "HELP",
        "menu.exit": "EXIT",
        # Abas de settings
        "settings.tab_general": "general",
        # Op\u00e7\u00f5es de settings
        "settings.opt_language": "Language",
        "settings.desc_language": (
            "Sets the interface language.\n\n"
            "Use \u2190 \u2192 to cycle through\n"
            "available languages.\n\n"
            "Change is applied\nimmediately."
        ),
        "settings.saved_at": "Config at:",
        # Console / compila\u00e7\u00e3o
        "compile.select_file": "\u274c Select a file and a template to compile.",
        "compile.select_watch": "\u274c Select a file and a template before enabling Watch Mode.",
        "compile.start": "\U0001f680 Compiling",
        "compile.error": "\u274c Unexpected error",
        "watch.on": "\U0001f52d Watch Mode enabled for",
        "watch.off": "\U0001f4a4 Watch Mode disabled.",
        # Border titles
        "panel.files": "\u2022 Files",
        "panel.config": "\u2022 Settings",
        "panel.preview": "\u2022 Preview",
        "panel.console": "\u2022 Console",
        "panel.template_label": "Set the PDF Template",
        # Bot\u00f5es
        "btn.compile": "COMPILE",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "File     : \u2014",
        "status.template": "Template : \u2014",
        # Help
        "help.title": "HELP & SHORTCUTS",
        "help.footer": "Press ESC to go back",
        "help.bindings_title": "Key Bindings:",
        "help.flow_title": "Workflow:",
        "help.flow_1": "1. Select a .md file in the left panel",
        "help.flow_2": "2. Choose a template (tcc, artigo, projeto)",
        "help.flow_3": "3. Press c or click COMPILE",
        "help.flow_4": "4. Follow the progress in the console below",
        # log_translator
        "log.config_reading": "\u2699\ufe0f Config: reading configuration files",
        "log.config_file": "\u2699\ufe0f Config: {path}",
        "log.output_written": "\U0001f4c4 Output written: {fmt} ({pages} pages)",
        "log.applying_rule": "\U0001f527 Applying rule: {name}",
        "log.latexmk_version": "\u2139\ufe0f Latexmk {ver}",
        "log.refs_changed": "\U0001f504 References changed, recompiling...",
        "log.bib_file": "\U0001f4da Bibliography file: {fname}",
        "log.engine_xetex": "\u2139\ufe0f Engine: XeTeX {ver}",
        "log.engine_bibtex": "\u2139\ufe0f Engine: BibTeX {ver}",
        "log.doc_class": "\U0001f4c4 Class: {cls}{ver}",
        "log.run_n": "\U0001f504 Compilation {n} \u2014 rule: {rule}",
        "log.running_xelatex": "\u25b6\ufe0f xelatex output.tex",
        "log.running_bibtex": "\u25b6\ufe0f bibtex {arg}",
        "log.running_cmd": "\u25b6\ufe0f {cmd}",
        "log.latex_error": "\u274c LaTeX Error: {msg}",
        "log.error": "\u274c {msg}",
        "log.line_ref_ctx": "   \u21b3 line {n}: {ctx}",
        "log.line_ref": "   \u21b3 line {n}",
        "log.overfull": "\u26a0\ufe0f Overwide text ({amount}) at lines {l1}\u2013{l2}",
        "log.pkg_warn": "\u26a0\ufe0f [{pkg}] {msg}",
        "log.latex_warn": "\u26a0\ufe0f {msg}",
        "log.bib_style": "\U0001f4dd Bibliography style: {sty}",
        "log.bib_db": "\U0001f4da Database: {db}",
        "log.no_citations": "\u2139\ufe0f No citations found in the document",
        "log.bib_errors": "\u274c {msg}",
        "log.refs_empty": "\u26a0\ufe0f Empty bibliography section",
        "log.latexmk_generic": "\U0001f527 Latexmk: {msg}",
    },
}

_current: str = "pt_BR"


def set_language(lang: str) -> None:
    global _current
    if lang in SUPPORTED_LANGUAGES:
        _current = lang


def get_language() -> str:
    return _current


def t(key: str) -> str:
    return (
        _STRINGS.get(_current, {}).get(key)
        or _STRINGS["pt_BR"].get(key, key)
    )

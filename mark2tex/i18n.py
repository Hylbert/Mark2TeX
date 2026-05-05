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
        # Opções
        "settings.opt_language": "Idioma",
        "settings.desc_language": (
            "Define o idioma da interface.\n\n"
            "Use ← → para alternar entre\n"
            "os idiomas disponíveis.\n\n"
            "A alteração é aplicada\nimediatamente."
        ),
        "settings.opt_theme": "Tema",
        "settings.desc_theme": (
            "Define o tema visual da interface.\n\n"
            "Use ← → para alternar entre\n"
            "os temas disponíveis.\n\n"
            "Default, Nord, Dracula,\nSolarized, Gruvbox."
        ),
        "settings.saved_at": "Config em:",
        # Console / compilação
        "compile.select_file": "✗ Selecione um arquivo e um template para compilar.",
        "compile.select_watch": "✗ Selecione um arquivo e um template antes de ativar o Watch Mode.",
        "compile.start": "🚀 Compilando",
        "compile.error": "✗ Erro inesperado",
        "watch.on": "🔭 Watch Mode ativado para",
        "watch.off": "💤 Watch Mode desativado.",
        # Border titles
        "panel.files": "• Arquivos",
        "panel.config": "• Configuração",
        "panel.preview": "• Preview",
        "panel.console": "• Console",
        "panel.template_label": "Defina o Template do Arquivo PDF",
        "panel.font_label": "Defina a Fonte do Documento",
        # Botões
        "btn.compile": "COMPILAR",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "Arquivo  : —",
        "status.template": "Template : —",
        "status.font": "Fonte    : — (padrão do template)",
        # Fonte
        "font.using": "Fonte selecionada:",
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
        "log.config_reading": "⚙️ Config: lendo arquivos de configuração",
        "log.config_file": "⚙️ Config: {path}",
        "log.output_written": "📄 Saída gerada: {fmt} ({pages} páginas)",
        "log.applying_rule": "🔧 Aplicando regra: {name}",
        "log.latexmk_version": "ℹ️ Latexmk {ver}",
        "log.refs_changed": "🔄 Referências alteradas, recompilando...",
        "log.bib_file": "📚 Arquivo de referências: {fname}",
        "log.engine_xetex": "ℹ️ Motor: XeTeX {ver}",
        "log.engine_bibtex": "ℹ️ Motor: BibTeX {ver}",
        "log.doc_class": "📄 Classe: {cls}{ver}",
        "log.run_n": "🔄 Compilação {n} — regra: {rule}",
        "log.running_xelatex": "▶️ xelatex output.tex",
        "log.running_bibtex": "▶️ bibtex {arg}",
        "log.running_cmd": "▶️ {cmd}",
        "log.latex_error": "✗ Erro LaTeX: {msg}",
        "log.error": "✗ {msg}",
        "log.line_ref_ctx": "   ↳ linha {n}: {ctx}",
        "log.line_ref": "   ↳ linha {n}",
        "log.overfull": "⚠️ Texto largo ({amount}) nas linhas {l1}–{l2}",
        "log.pkg_warn": "⚠️ [{pkg}] {msg}",
        "log.latex_warn": "⚠️ {msg}",
        "log.bib_style": "📝 Estilo bibliográfico: {sty}",
        "log.bib_db": "📚 Base de dados: {db}",
        "log.no_citations": "ℹ️ Nenhuma citação encontrada no documento",
        "log.bib_errors": "✗ {msg}",
        "log.refs_empty": "⚠️ Seção de referências vazia",
        "log.latexmk_generic": "🔧 Latexmk: {msg}",
        # Onboarding
        "onboarding.title": " 👋  Bem-vindo ao Mark2TeX ",
        "onboarding.welcome": "Parece que é a primeira vez que você executa o Mark2TeX.",
        "onboarding.what": (
            "O Mark2TeX converte arquivos Markdown em PDFs profissionais\n"
            "usando templates LaTeX — tudo rodando dentro de um container Docker."
        ),
        "onboarding.steps": (
            "  1. Selecione ou crie um arquivo .md no painel de arquivos\n"
            "  2. Escolha um template (TCC, Artigo IEEE, Documento Técnico…)\n"
            "  3. Pressione [c] ou clique em COMPILAR\n"
            "  4. O PDF gerado aparecerá no diretório atual"
        ),
        "onboarding.hint_init": (
            "💡 Dica: rode  mark2tex init  para copiar um template de exemplo"
            " para o diretório atual."
        ),
        "onboarding.btn_start": "  Entendi, vamos começar!  ",
        "onboarding.footer": "ESC / Enter — fechar esta tela",
    },
    "en_US": {
        # Menu Global
        "menu.settings": "SETTINGS",
        "menu.help": "HELP",
        "menu.exit": "EXIT",
        # Abas de settings
        "settings.tab_general": "general",
        # Opções
        "settings.opt_language": "Language",
        "settings.desc_language": (
            "Sets the interface language.\n\n"
            "Use ← → to cycle through\n"
            "available languages.\n\n"
            "Change is applied\nimmediately."
        ),
        "settings.opt_theme": "Theme",
        "settings.desc_theme": (
            "Sets the visual theme.\n\n"
            "Use ← → to cycle through\n"
            "available themes.\n\n"
            "Default, Nord, Dracula,\nSolarized, Gruvbox."
        ),
        "settings.saved_at": "Config at:",
        # Console / compilação
        "compile.select_file": "✗ Select a file and a template to compile.",
        "compile.select_watch": "✗ Select a file and a template before enabling Watch Mode.",
        "compile.start": "🚀 Compiling",
        "compile.error": "✗ Unexpected error",
        "watch.on": "🔭 Watch Mode enabled for",
        "watch.off": "💤 Watch Mode disabled.",
        # Border titles
        "panel.files": "• Files",
        "panel.config": "• Settings",
        "panel.preview": "• Preview",
        "panel.console": "• Console",
        "panel.template_label": "Set the PDF Template",
        "panel.font_label": "Set the Document Font",
        # Botões
        "btn.compile": "COMPILE",
        "btn.watch_off": "WATCH: OFF",
        "btn.watch_on": "WATCH: ON",
        # Status
        "status.file": "File     : —",
        "status.template": "Template : —",
        "status.font": "Font     : — (template default)",
        # Fonte
        "font.using": "Selected font:",
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
        "log.config_reading": "⚙️ Config: reading configuration files",
        "log.config_file": "⚙️ Config: {path}",
        "log.output_written": "📄 Output written: {fmt} ({pages} pages)",
        "log.applying_rule": "🔧 Applying rule: {name}",
        "log.latexmk_version": "ℹ️ Latexmk {ver}",
        "log.refs_changed": "🔄 References changed, recompiling...",
        "log.bib_file": "📚 Bibliography file: {fname}",
        "log.engine_xetex": "ℹ️ Engine: XeTeX {ver}",
        "log.engine_bibtex": "ℹ️ Engine: BibTeX {ver}",
        "log.doc_class": "📄 Class: {cls}{ver}",
        "log.run_n": "🔄 Compilation {n} — rule: {rule}",
        "log.running_xelatex": "▶️ xelatex output.tex",
        "log.running_bibtex": "▶️ bibtex {arg}",
        "log.running_cmd": "▶️ {cmd}",
        "log.latex_error": "✗ LaTeX Error: {msg}",
        "log.error": "✗ {msg}",
        "log.line_ref_ctx": "   ↳ line {n}: {ctx}",
        "log.line_ref": "   ↳ line {n}",
        "log.overfull": "⚠️ Overwide text ({amount}) at lines {l1}–{l2}",
        "log.pkg_warn": "⚠️ [{pkg}] {msg}",
        "log.latex_warn": "⚠️ {msg}",
        "log.bib_style": "📝 Bibliography style: {sty}",
        "log.bib_db": "📚 Database: {db}",
        "log.no_citations": "ℹ️ No citations found in the document",
        "log.bib_errors": "✗ {msg}",
        "log.refs_empty": "⚠️ Empty bibliography section",
        "log.latexmk_generic": "🔧 Latexmk: {msg}",
        # Onboarding
        "onboarding.title": " 👋  Welcome to Mark2TeX ",
        "onboarding.welcome": "This looks like your first time running Mark2TeX.",
        "onboarding.what": (
            "Mark2TeX converts Markdown files into professional PDFs\n"
            "using LaTeX templates — everything runs inside a Docker container."
        ),
        "onboarding.steps": (
            "  1. Select or create a .md file in the file panel\n"
            "  2. Choose a template (TCC, IEEE Article, Technical Doc…)\n"
            "  3. Press [c] or click COMPILE\n"
            "  4. The generated PDF will appear in the current directory"
        ),
        "onboarding.hint_init": (
            "💡 Tip: run  mark2tex init  to copy a starter template"
            " into the current directory."
        ),
        "onboarding.btn_start": "  Got it, let's start!  ",
        "onboarding.footer": "ESC / Enter — close this screen",
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
    return _STRINGS.get(_current, {}).get(key) or _STRINGS["pt_BR"].get(key, key)

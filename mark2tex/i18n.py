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
            "Ainda não tem um arquivo .md? Clique em \"Inicializar projeto aqui\" abaixo\n"
            "e geraremos um exemplo pronto para editar. Ou, se preferir o terminal,\n"
            "rode  mark2tex init  e o arquivo aparecerá automaticamente no painel."
        ),
        "onboarding.btn_start": "  Entendi, vamos começar!  ",
        "onboarding.btn_init":  "  Inicializar projeto aqui  ",
        "onboarding.init_done": "✔ Pronto! Template '{template}' copiado — selecione o arquivo e compile.",
        "onboarding.init_done_renamed": (
            "✔ Pronto! Exemplo salvo como '{renamed}'\n"
            "(seu arquivo original foi preservado)."
        ),
        "onboarding.init_nothing": "⚠ Nenhum arquivo novo copiado — arquivos já existem no diretório.",
        "onboarding.init_error": "✗ Falha ao inicializar: {msg}",
        "onboarding.footer": "ESC / Enter — fechar esta tela",
        # YAML inject
        "yaml.title": " ⚙  Configuração necessária ",
        "yaml.body": (
            "O arquivo '{filename}' não tem cabeçalho de configuração YAML.\n\n"
            "O Mark2TeX vai adicionar um cabeçalho para o template '{template}'\n"
            "no início do arquivo para que ele possa ser compilado."
        ),
        "yaml.hint_restore": "Você pode desfazer isso a qualquer momento com: mark2tex restore <arquivo>",
        "yaml.btn_inject": "  Adicionar e compilar  ",
        "yaml.btn_cancel": "  Cancelar  ",
        "yaml.injected_ok": "✔ Cabeçalho YAML adicionado — compilando...",
        "yaml.injected_err": "✗ Não foi possível modificar o arquivo: {msg}",
        "yaml.no_frontmatter_badge": "⚠ sem YAML",
        "yaml.template_swapped": "✔ Cabeçalho atualizado para template '{template}'.",
        "yaml.template_swap_err": "✗ Não foi possível atualizar o cabeçalho: {msg}",
        # Uninstall
        "uninstall.image_removed":    "✔ Imagem {tag} removida.",
        "uninstall.image_not_found":  "  Imagem {tag} não encontrada, ignorando.",
        "uninstall.docker_error":     "✘ Erro ao acessar Docker: {error}",
        "uninstall.data_removed":     "✔ Dados do usuário removidos: {path}",
        "uninstall.data_not_found":   "  Dados do usuário não encontrados: {path}",
        "uninstall.config_removed":   "✔ Configurações removidas: {path}",
        "uninstall.config_not_found": "  Configurações não encontradas: {path}",
        "uninstall.pipx_hint":        "Execute `pipx uninstall mark2tex` para remover o pacote Python.",
        # Frontmatter validator
        "validator.parse_error": "⚠️ Não foi possível ler o cabeçalho YAML. Verifique se o arquivo começa com um bloco --- válido.",
        "validator.missing": "⚠️ Campo obrigatório ausente ou vazio: '{field}'.",
        "validator.placeholder": "⚠️ O campo '{field}' ainda contém o valor padrão. Preencha antes de compilar.",
        "validator.template_mismatch": "⚠️ O cabeçalho declara template '{fm_template}' mas a TUI tem '{selected}' selecionado. Atualize o cabeçalho ou escolha o template correto.",
        "validator.invalid_lang": "⚠️ O valor de 'lang' ({lang}) não é reconhecido. Valores aceitos: {accepted}.",
        "validator.warnings_header": "── Avisos do cabeçalho YAML (a compilação continua) ──",
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
            "Don't have a .md file yet? Click \"Initialise project here\" below\n"
            "and we'll generate a ready-to-edit example for you. Or, if you prefer\n"
            "the terminal, run  mark2tex init  and the file will appear in the panel."
        ),
        "onboarding.btn_start": "  Got it, let's start!  ",
        "onboarding.btn_init":  "  Initialise project here  ",
        "onboarding.init_done": "✔ Done! Template '{template}' copied — select the file and compile.",
        "onboarding.init_done_renamed": (
            "✔ Done! Example saved as '{renamed}'\n"
            "(your original file was preserved)."
        ),
        "onboarding.init_nothing": "⚠ Nothing new to copy — files already exist in this directory.",
        "onboarding.init_error": "✗ Failed to initialise: {msg}",
        "onboarding.footer": "ESC / Enter — close this screen",
        # YAML inject
        "yaml.title": " ⚙  Configuration required ",
        "yaml.body": (
            "The file '{filename}' has no YAML configuration header.\n\n"
            "Mark2TeX will add a header for template '{template}'\n"
            "at the top of the file so it can be compiled."
        ),
        "yaml.hint_restore": "You can undo this at any time with: mark2tex restore <file>",
        "yaml.btn_inject": "  Add header and compile  ",
        "yaml.btn_cancel": "  Cancel  ",
        "yaml.injected_ok": "✔ YAML header added — compiling...",
        "yaml.injected_err": "✗ Could not modify the file: {msg}",
        "yaml.no_frontmatter_badge": "⚠ no YAML",
        "yaml.template_swapped": "✔ Header updated to template '{template}'.",
        "yaml.template_swap_err": "✗ Could not update the header: {msg}",
        # Uninstall
        "uninstall.image_removed":    "✔ Image {tag} removed.",
        "uninstall.image_not_found":  "  Image {tag} not found, skipping.",
        "uninstall.docker_error":     "✘ Docker error: {error}",
        "uninstall.data_removed":     "✔ User data removed: {path}",
        "uninstall.data_not_found":   "  User data not found: {path}",
        "uninstall.config_removed":   "✔ Config removed: {path}",
        "uninstall.config_not_found": "  Config not found: {path}",
        "uninstall.pipx_hint":        "Run `pipx uninstall mark2tex` to remove the Python package.",
        # Frontmatter validator
        "validator.parse_error": "⚠️ Could not read the YAML header. Make sure the file starts with a valid --- block.",
        "validator.missing": "⚠️ Required field missing or empty: '{field}'.",
        "validator.placeholder": "⚠️ Field '{field}' still contains the default placeholder. Fill it in before compiling.",
        "validator.template_mismatch": "⚠️ Header declares template '{fm_template}' but the TUI has '{selected}' selected. Update the header or re-select the correct template.",
        "validator.invalid_lang": "⚠️ The 'lang' value ({lang}) is not recognised. Accepted values: {accepted}.",
        "validator.warnings_header": "── YAML header warnings (compilation continues) ──",
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

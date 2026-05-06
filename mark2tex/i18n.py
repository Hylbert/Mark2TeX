from __future__ import annotations

_LANG = "pt_BR"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt_BR": {
        # ── status panel ────────────────────────────────────────────────────
        "status.file":     "Arquivo  : (nenhum selecionado)",
        "status.template": "Template : (nenhum selecionado)",
        "status.font":     "Fonte    : (padrão)",
        # ── panels ──────────────────────────────────────────────────────────
        "panel.files":          "Arquivos",
        "panel.config":         "Configuração",
        "panel.preview":        "Pré-visualização",
        "panel.console":        "Console",
        "panel.template_label": "Templates",
        "panel.font_label":     "Fontes",
        # ── buttons ─────────────────────────────────────────────────────────
        "btn.compile":   "COMPILAR",
        "btn.watch_on":  "WATCH ATIVO",
        "btn.watch_off": "WATCH MODE",
        # ── compile messages ────────────────────────────────────────────────
        "compile.start":       "Compilando",
        "compile.select_file": "⚠ Selecione um arquivo e um template antes de compilar.",
        "compile.select_watch":"⚠ Selecione um arquivo e um template antes de ativar o watch.",
        "compile.error":       "Erro durante a compilação",
        # ── watch ────────────────────────────────────────────────────────────
        "watch.on":  "Watch mode ativado para",
        "watch.off": "Watch mode desativado.",
        # ── font ─────────────────────────────────────────────────────────────
        "font.using": "Usando fonte:",
        # ── menu ─────────────────────────────────────────────────────────────
        "menu.settings": "CONFIGURAÇÕES",
        "menu.help":     "AJUDA",
        "menu.exit":     "SAIR",
        # ── help screen ──────────────────────────────────────────────────────
        "help.title":         "AJUDA — MARK2TEX",
        "help.bindings_title":"Atalhos de teclado",
        "help.flow_title":    "Fluxo de uso",
        "help.flow_1":        "1. Selecione um arquivo .md no painel esquerdo.",
        "help.flow_2":        "2. Escolha um template (tcc-abnt, artigo-ieee...).",
        "help.flow_3":        "3. Opcionalmente, selecione uma fonte.",
        "help.flow_4":        "4. Pressione C para compilar ou W para Watch Mode.",
        "help.footer":        "Mark2TeX — Markdown para PDF acadêmico com qualidade LaTeX.",
        # ── settings screen ───────────────────────────────────────────────────
        "settings.title":        "CONFIGURAÇÕES",
        "settings.language":      "Idioma",
        "settings.theme":         "Tema",
        "settings.saved":         "Configurações salvas!",
        "settings.close":         "Fechar",
        # ── yaml inject ──────────────────────────────────────────────────────
        "yaml.title":        "YAML Frontmatter Ausente",
        "yaml.body":         "O arquivo '{file}' não possui frontmatter YAML.\nDeseja injetar o cabeçalho para o template '{template}'?\n\nUm backup será salvo em ~/.local/share/mark2tex/backups/",
        "yaml.confirm":      "Injetar e Compilar",
        "yaml.cancel":       "Cancelar",
        "yaml.injected_ok":  "✔ Frontmatter YAML injetado com sucesso.",
        "yaml.injected_err": "✘ Erro ao injetar frontmatter: {msg}",
        # ── onboarding ───────────────────────────────────────────────────────
        "onboarding.title":         "Bem-vindo ao Mark2TeX!",
        "onboarding.subtitle":      "Markdown → PDF acadêmico com qualidade LaTeX",
        "onboarding.step1":         "1. Selecione um arquivo .md no painel esquerdo",
        "onboarding.step2":         "2. Escolha um template e uma fonte",
        "onboarding.step3":         "3. Pressione C para compilar",
        "onboarding.step4":         "4. O PDF aparece na mesma pasta do .md",
        "onboarding.hint_init":     "Ainda não tem um arquivo .md?\nClique em 'Inicializar projeto aqui' ou rode mark2tex init no terminal.",
        "onboarding.btn_start":     "Entendido, vamos começar!",
        "onboarding.btn_init":      "Inicializar projeto aqui",
        "onboarding.init_done":     "✔ Projeto inicializado! Arquivo copiado para este diretório.",
        "onboarding.init_done_renamed": "✔ Arquivo salvo como '{name}' (original preservado).",
        "onboarding.init_error":    "✘ Erro ao inicializar: {error}",
        # ── check ────────────────────────────────────────────────────────────
        "check.label.mark2tex":     "Mark2TeX",
        "check.label.docker_bin":   "Docker (binário)",
        "check.label.docker_daemon":"Docker (daemon)",
        "check.label.docker_image": "Imagem mark2tex",
        "check.label.pandoc":       "Pandoc",
        "check.label.python":       "Python",
        "check.label.disk":         "Espaço em disco",
        "check.ok":                 "ok",
        "check.warning":            "aviso",
        "check.error":              "erro",
        "check.summary_ok":         "Tudo certo — pronto para compilar.",
        "check.summary_warn":       "Verifique os avisos acima antes de compilar.",
        "check.summary_error":      "Corrija os erros acima antes de compilar.",
        "check.hint_warn":          "Revise os avisos acima antes de compilar.",
        # ── uninstall ────────────────────────────────────────────────────────
        "uninstall.image_removed":   "✔ Imagem {tag} removida.",
        "uninstall.image_not_found": "  Imagem {tag} não encontrada, ignorando.",
        "uninstall.docker_error":    "✘ Erro ao acessar Docker: {error}",
        "uninstall.data_removed":    "✔ Dados do usuário removidos: {path}",
        "uninstall.data_not_found":  "  Dados do usuário não encontrados: {path}",
        "uninstall.config_removed":  "✔ Configurações removidas: {path}",
        "uninstall.config_not_found":"  Configurações não encontradas: {path}",
        "uninstall.pipx_hint":       "Execute `pipx uninstall mark2tex` para remover o pacote Python.",
    },
    "en_US": {
        # ── status panel ────────────────────────────────────────────────────
        "status.file":     "File     : (none selected)",
        "status.template": "Template : (none selected)",
        "status.font":     "Font     : (default)",
        # ── panels ──────────────────────────────────────────────────────────
        "panel.files":          "Files",
        "panel.config":         "Configuration",
        "panel.preview":        "Preview",
        "panel.console":        "Console",
        "panel.template_label": "Templates",
        "panel.font_label":     "Fonts",
        # ── buttons ─────────────────────────────────────────────────────────
        "btn.compile":   "COMPILE",
        "btn.watch_on":  "WATCH ON",
        "btn.watch_off": "WATCH MODE",
        # ── compile messages ────────────────────────────────────────────────
        "compile.start":        "Compiling",
        "compile.select_file":  "⚠ Select a file and a template before compiling.",
        "compile.select_watch": "⚠ Select a file and a template before enabling watch.",
        "compile.error":        "Error during compilation",
        # ── watch ────────────────────────────────────────────────────────────
        "watch.on":  "Watch mode enabled for",
        "watch.off": "Watch mode disabled.",
        # ── font ─────────────────────────────────────────────────────────────
        "font.using": "Using font:",
        # ── menu ─────────────────────────────────────────────────────────────
        "menu.settings": "SETTINGS",
        "menu.help":     "HELP",
        "menu.exit":     "EXIT",
        # ── help screen ──────────────────────────────────────────────────────
        "help.title":         "HELP — MARK2TEX",
        "help.bindings_title":"Keyboard shortcuts",
        "help.flow_title":    "Usage flow",
        "help.flow_1":        "1. Select a .md file in the left panel.",
        "help.flow_2":        "2. Choose a template (tcc-abnt, artigo-ieee...).",
        "help.flow_3":        "3. Optionally select a font.",
        "help.flow_4":        "4. Press C to compile or W for Watch Mode.",
        "help.footer":        "Mark2TeX — Markdown to academic PDF with LaTeX quality.",
        # ── settings screen ───────────────────────────────────────────────────
        "settings.title":   "SETTINGS",
        "settings.language": "Language",
        "settings.theme":    "Theme",
        "settings.saved":    "Settings saved!",
        "settings.close":    "Close",
        # ── yaml inject ──────────────────────────────────────────────────────
        "yaml.title":        "Missing YAML Frontmatter",
        "yaml.body":         "File '{file}' has no YAML frontmatter.\nInject the header for template '{template}'?\n\nA backup will be saved to ~/.local/share/mark2tex/backups/",
        "yaml.confirm":      "Inject & Compile",
        "yaml.cancel":       "Cancel",
        "yaml.injected_ok":  "✔ YAML frontmatter injected successfully.",
        "yaml.injected_err": "✘ Error injecting frontmatter: {msg}",
        # ── onboarding ───────────────────────────────────────────────────────
        "onboarding.title":         "Welcome to Mark2TeX!",
        "onboarding.subtitle":      "Markdown → academic PDF with LaTeX quality",
        "onboarding.step1":         "1. Select a .md file in the left panel",
        "onboarding.step2":         "2. Choose a template and a font",
        "onboarding.step3":         "3. Press C to compile",
        "onboarding.step4":         "4. The PDF appears in the same folder as your .md",
        "onboarding.hint_init":     "Don't have a .md file yet?\nClick 'Initialise project here' or run mark2tex init in the terminal.",
        "onboarding.btn_start":     "Got it, let's start!",
        "onboarding.btn_init":      "Initialise project here",
        "onboarding.init_done":     "✔ Project initialised! File copied to this directory.",
        "onboarding.init_done_renamed": "✔ File saved as '{name}' (original preserved).",
        "onboarding.init_error":    "✘ Init error: {error}",
        # ── check ────────────────────────────────────────────────────────────
        "check.label.mark2tex":     "Mark2TeX",
        "check.label.docker_bin":   "Docker binary",
        "check.label.docker_daemon":"Docker daemon",
        "check.label.docker_image": "Image mark2tex",
        "check.label.pandoc":       "Pandoc",
        "check.label.python":       "Python",
        "check.label.disk":         "Disk space",
        "check.ok":                 "ok",
        "check.warning":            "warning",
        "check.error":              "error",
        "check.summary_ok":         "All good — ready to compile.",
        "check.summary_warn":       "Review the warnings above before compiling.",
        "check.summary_error":      "Fix the errors above before compiling.",
        "check.hint_warn":          "Review the warnings above before compiling.",
        # ── uninstall ────────────────────────────────────────────────────────
        "uninstall.image_removed":   "✔ Image {tag} removed.",
        "uninstall.image_not_found": "  Image {tag} not found, skipping.",
        "uninstall.docker_error":    "✘ Docker error: {error}",
        "uninstall.data_removed":    "✔ User data removed: {path}",
        "uninstall.data_not_found":  "  User data not found: {path}",
        "uninstall.config_removed":  "✔ Config removed: {path}",
        "uninstall.config_not_found":"  Config not found: {path}",
        "uninstall.pipx_hint":       "Run `pipx uninstall mark2tex` to remove the Python package.",
    },
}


def set_language(lang: str) -> None:
    global _LANG
    _LANG = lang if lang in TRANSLATIONS else "pt_BR"


def t(key: str) -> str:
    return TRANSLATIONS.get(_LANG, TRANSLATIONS["pt_BR"]).get(
        key,
        TRANSLATIONS["pt_BR"].get(key, key),
    )

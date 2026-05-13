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
        "log.error_at_line_ctx": "✗ {msg} — linha {n}: {ctx}",
        "log.error_at_line": "✗ {msg} — linha {n}",
        "log.overfull": "⚠️ Texto largo ({amount}) nas linhas {l1}–{l2}",
        "log.underfull": "⚠️ Texto com espaçamento excessivo ({amount}) nas linhas {l1}–{l2}",
        "log.pkg_warn": "⚠️ [{pkg}] {msg}",
        "log.latex_warn": "⚠️ {msg}",
        "log.undefined_refs": "⚠️ Há referências indefinidas no documento — recompile após resolver",
        "log.bib_style": "📝 Estilo bibliográfico: {sty}",
        "log.bib_db": "📚 Base de dados: {db}",
        "log.no_citations": "ℹ️ Nenhuma citação encontrada no documento",
        "log.bib_errors": "✗ {msg}",
        "log.bib_empty_field": "⚠️ [BibTeX] Campo '{field}' vazio na entrada '{entry}'",
        "log.bib_missing_field": "⚠️ [BibTeX] Campo obrigatório '{field}' ausente na entrada '{entry}'",
        "log.bib_warn": "⚠️ [BibTeX] {msg}",
        "log.refs_empty": "⚠️ Seção de referências vazia",
        "log.latexmk_generic": "🔧 Latexmk: {msg}",
        "log.latexmk_force_mode": "⚠️ Latexmk: erros encontrados no modo forçado — compilação continuada",
        "log.fontspec_error": "✗ Erro de fonte [{code}]: {hint}",
        # log.hint_* — dicas acionáveis para erros LaTeX/XeLaTeX
        "log.hint_undefined_cmd": "verifique typo no comando ou \\usepackage necessário",
        "log.hint_math_mode": "use $...$ ao redor de expressões matemáticas",
        "log.hint_math_display": "verifique se o ambiente de equação está fechado",
        "log.hint_missing_open_brace": "adicione { de abertura faltando",
        "log.hint_missing_close_brace": "adicione } de fechamento faltando",
        "log.hint_extra_brace": "chaves ou $ desbalanceados — revise o trecho",
        "log.hint_too_many_braces": "há um } sem { correspondente",
        "log.hint_runaway_arg": "argumento sem fechar — verifique as chaves {}",
        "log.hint_unclosed_env": "ambiente ou chave { não fechado antes do fim do arquivo",
        "log.hint_blank_in_arg": "linha em branco dentro de argumento de comando",
        "log.hint_missing_begin_doc": "texto antes de \\begin{document}",
        "log.hint_usepackage_after_begin": "\\usepackage só pode ser usado no preâmbulo",
        "log.hint_cmd_already_defined": "use \\renewcommand para redefinir um comando existente",
        "log.hint_option_clash": "mesmo pacote carregado com opções conflitantes",
        "log.hint_env_undefined": "ambiente não definido — verifique \\usepackage necessário",
        "log.hint_too_many_floats": "adicione \\clearpage para liberar figuras/tabelas acumuladas",
        "log.hint_capacity_exceeded": "limite interno do TeX excedido — simplifique o documento",
        "log.hint_emergency_stop": "compilação interrompida — veja o erro anterior no log",
        "log.hint_file_not_found": "arquivo ou pacote não encontrado — verifique o nome ou instale com tlmgr",
        "log.hint_no_counter": "contador referenciado antes de ser criado com \\newcounter",
        "log.hint_double_subscript": "use chaves: a_{bc} em vez de a_b_c",
        "log.hint_double_superscript": "use chaves: a^{bc} em vez de a^b^c",
        "log.hint_misplaced_tab": "& usado fora de tabela, array ou align",
        "log.hint_extra_right": "\\right sem \\left correspondente",
        "log.hint_missing_delimiter": "\\left sem delimitador válido — use \\left( ou \\left.",
        "log.hint_display_math": "linha em branco dentro de equação — verifique \\[ \\]",
        "log.hint_dimension_large": "valor de comprimento muito grande — verifique a unidade",
        "log.hint_arithmetic_overflow": "overflow em cálculo — simplifique a expressão",
        "log.hint_counter_large": "contador excede o máximo — verifique listas ou notas de rodapé",
        "log.hint_missing_number": "número ou comprimento faltando no argumento",
        "log.hint_illegal_unit": "unidade de medida inválida — use pt, cm, mm, em, ex, etc.",
        "log.hint_bad_math_delim": "\\[ sem \\] ou \\( sem \\) correspondente",
        "log.hint_verb_newline": "\\verb não pode ter quebra de linha interna",
        "log.hint_caption_outside_float": "\\caption só pode ser usado dentro de figure ou table",
        "log.hint_missing_item": "\\item faltando no início da lista",
        "log.hint_lonely_item": "\\item fora de ambiente de lista",
        "log.hint_too_nested": "listas aninhadas além de 4 níveis",
        "log.hint_not_outer_par": "float dentro de minipage, footnote ou outro ambiente secundário",
        "log.hint_nfss": "sistema NFSS de fontes mal configurado — verifique fontenc/fontspec",
        "log.hint_cant_find_file": "arquivo não encontrado — verifique o caminho ou nome",
        "log.hint_cant_write_file": "sem permissão de escrita — o PDF pode estar aberto em outro programa",
        "log.hint_invalid_char": "caractere inválido no arquivo — verifique o encoding (use UTF-8)",
        "log.hint_illegal_param": "# mal usado — em URLs use \\#; em \\newcommand declare [N] parâmetros",
        "log.hint_wrong_driver": "driver PDF conflitante com hyperref + XeLaTeX",
        "log.hint_floats_lost": "float dentro de minipage ou footnote — mova para fora",
        "log.hint_bad_line_vector": "argumento inválido para \\line ou \\vector no ambiente picture",
        "log.hint_internal_bug": "erro interno do TeX — atualize a distribuição ou isole o problema",
        "log.hint_font_not_found": "fonte não encontrada — verifique o nome exato ou instale a fonte no sistema",
        "log.hint_font_no_shape": "variante bold/italic/etc. não disponível para esta fonte",
        "log.hint_font_feature": "feature OpenType não suportada por esta fonte",
        "log.hint_font_script": "script OpenType inexistente nesta fonte",
        "log.hint_font_language": "idioma OpenType não disponível nesta fonte",
        # build.sh — mensagens de status do script de compilação
        "build.starting": "🚀 Iniciando compilação de {file} com template {template}...",
        "build.md_converted": "✅ Markdown convertido para LaTeX.",
        "build.full_build": "🔧 Build completo: nenhum cache anterior encontrado.",
        "build.incremental": "⚡ Build incremental: reutilizando cache da compilação anterior.",
        "build.compiling_pdf": "🔨 Compilando PDF com latexmk...",
        "build.pdf_ok": "✅ PDF gerado com sucesso: {filename}",
        "build.pdf_error": "❌ Erro: PDF não foi gerado.",
        "build.complete": "🎉 Compilação concluída!",
        "build.cleaning": "🧹 Limpando arquivos temporários de build...",
        "build.warn_no_state": "⚠️ Build falhou sem estado do latexmk — limpando cache para retry limpo.",
        "build.warn_state_kept": "⚠️ Build falhou mas estado do latexmk preservado — próxima execução será incremental.",
        "build.warn_missing_image": "⚠️ Imagem não encontrada: {img} — substituída por marcador no documento.",
        # Onboarding
        "onboarding.title": " 👋  Bem-vindo ao Mark2TeX ",
        "onboarding.welcome": "Parece que é a primeira vez que você usa o Mark2TeX.",
        "onboarding.what": (
            "O Mark2TeX converte arquivos Markdown em PDFs profissionais\n"
            "usando templates LaTeX — tudo roda dentro de um container Docker."
        ),
        "onboarding.steps": (
            "  1. Selecione ou crie um arquivo .md no painel de arquivos\n"
            "  2. Escolha um template (TCC, Artigo IEEE, Doc. Técnica…)\n"
            "  3. Pressione [c] ou clique em COMPILAR\n"
            "  4. O PDF gerado aparecerá no diretório atual"
        ),
        "onboarding.hint_init": (
            "Não tem um arquivo .md ainda? Clique em \"Inicializar projeto aqui\" abaixo\n"
            "e geraremos um exemplo pronto para edição. Ou, se preferir o terminal,\n"
            "rode  mark2tex init  e o arquivo aparecerá no painel."
        ),
        "onboarding.btn_start": "  Entendi, vamos começar!  ",
        "onboarding.btn_init":  "  Inicializar projeto aqui  ",
        "onboarding.init_done": "✔ Pronto! Template '{template}' copiado — selecione o arquivo e compile.",
        "onboarding.init_done_renamed": (
            "✔ Pronto! Exemplo salvo como '{renamed}'\n"
            "(seu arquivo original foi preservado)."
        ),
        "onboarding.init_nothing": "⚠ Nada novo para copiar — arquivos já existem neste diretório.",
        "onboarding.init_error": "✗ Falha ao inicializar: {msg}",
        "onboarding.footer": "ESC / Enter — fechar esta tela",
        # YAML inject
        "yaml.title": " ⚙  Configuração necessária ",
        "yaml.body": (
            "O arquivo '{filename}' não tem cabeçalho de configuração YAML.\n\n"
            "O Mark2TeX adicionará um cabeçalho para o template '{template}'\n"
            "no topo do arquivo para que ele possa ser compilado."
        ),
        "yaml.hint_restore": "Você pode desfazer isso a qualquer momento com: mark2tex restore <arquivo>",
        "yaml.btn_inject": "  Adicionar cabeçalho e compilar  ",
        "yaml.btn_cancel": "  Cancelar  ",
        "yaml.injected_ok": "✔ Cabeçalho YAML adicionado — compilando...",
        "yaml.injected_err": "✗ Não foi possível modificar o arquivo: {msg}",
        "yaml.no_frontmatter_badge": "⚠ sem YAML",
        "yaml.template_swapped": "✔ Cabeçalho atualizado para o template '{template}'.",
        "yaml.template_swap_err": "✗ Não foi possível atualizar o cabeçalho: {msg}",
        # Uninstall
        "uninstall.image_removed":    "✔ Imagem {tag} removida.",
        "uninstall.image_not_found":  "  Imagem {tag} não encontrada, pulando.",
        "uninstall.docker_error":     "✘ Erro Docker: {error}",
        "uninstall.data_removed":     "✔ Dados do usuário removidos: {path}",
        "uninstall.data_not_found":   "  Dados do usuário não encontrados: {path}",
        "uninstall.config_removed":   "✔ Config removida: {path}",
        "uninstall.config_not_found": "  Config não encontrada: {path}",
        "uninstall.cache_removed":    "✔ Cache removido: {path}",
        "uninstall.cache_not_found":  "  Cache não encontrado: {path}",
        "uninstall.pipx_hint":        "Execute `pipx uninstall mark2tex` para remover o pacote Python.",
        # Clean
        "clean.removed": "✔ Cache removido: {path}",
        "clean.error":   "✗ Falha ao remover cache: {path}",
        # Frontmatter validator
        "validator.parse_error": "⚠️ Não foi possível ler o cabeçalho YAML. Verifique se o arquivo começa com um bloco --- válido.",
        "validator.missing": "⚠️ Campo obrigatório ausente ou vazio: '{field}'.",
        "validator.placeholder": "⚠️ O campo '{field}' ainda contém o valor padrão. Preencha antes de compilar.",
        "validator.template_mismatch": "⚠️ O cabeçalho declara template '{fm_template}' mas a TUI tem '{selected}' selecionado. Atualize o cabeçalho ou escolha o template correto.",
        "validator.invalid_lang": "⚠️ O valor de 'lang' ({lang}) não é reconhecido. Valores aceitos: {accepted}.",
        "validator.warnings_header": "── Avisos do cabeçalho YAML (a compilação continua) ──",
        # Info panel (tabbed preview)
        "info.tab_markdown":   "Markdown",
        "info.tab_pdf":        "Info PDF",
        "info.pages":          "Páginas geradas:",
        "info.template":       "Template:",
        "info.last_compiled":  "Última compilação:",
        "info.status":         "Status:",
        "info.status_success": "Sucesso",
        "info.status_error":   "Erro",
        "info.status_pending": "Aguardando compilação",
        "info.structure":      "Estrutura do documento",
        "info.no_sections":    "Nenhuma seção encontrada.",
        "info.warnings":       "Avisos",
        "info.no_warnings":    "Nenhum aviso.",
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
        "help.bindings_title": "Keyboard shortcuts:",
        "help.flow_title": "Usage flow:",
        "help.flow_1": "1. Select a .md file in the left panel",
        "help.flow_2": "2. Choose a template (tcc, article, project)",
        "help.flow_3": "3. Press c or click COMPILE",
        "help.flow_4": "4. Follow the progress in the console below",
        # log_translator
        "log.config_reading": "⚙️ Config: reading configuration files",
        "log.config_file": "⚙️ Config: {path}",
        "log.output_written": "📄 Output written: {fmt} ({pages} pages)",
        "log.applying_rule": "🔧 Applying rule: {name}",
        "log.latexmk_version": "ℹ️ Latexmk {ver}",
        "log.refs_changed": "🔄 References changed, recompiling...",
        "log.bib_file": "📚 References file: {fname}",
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
        "log.error_at_line_ctx": "✗ {msg} — line {n}: {ctx}",
        "log.error_at_line": "✗ {msg} — line {n}",
        "log.overfull": "⚠️ Overfull text ({amount}) on lines {l1}–{l2}",
        "log.underfull": "⚠️ Underfull text ({amount}) on lines {l1}–{l2}",
        "log.pkg_warn": "⚠️ [{pkg}] {msg}",
        "log.latex_warn": "⚠️ {msg}",
        "log.undefined_refs": "⚠️ There are undefined references — recompile after fixing them",
        "log.bib_style": "📝 Bibliography style: {sty}",
        "log.bib_db": "📚 Database: {db}",
        "log.no_citations": "ℹ️ No citations found in the document",
        "log.bib_errors": "✗ {msg}",
        "log.bib_empty_field": "⚠️ [BibTeX] Empty field '{field}' in entry '{entry}'",
        "log.bib_missing_field": "⚠️ [BibTeX] Required field '{field}' missing in entry '{entry}'",
        "log.bib_warn": "⚠️ [BibTeX] {msg}",
        "log.refs_empty": "⚠️ Empty references section",
        "log.latexmk_generic": "🔧 Latexmk: {msg}",
        "log.latexmk_force_mode": "⚠️ Latexmk: errors encountered in force mode — compilation continued",
        "log.fontspec_error": "✗ Font error [{code}]: {hint}",
        # log.hint_*
        "log.hint_undefined_cmd": "check for a typo or a missing \\usepackage",
        "log.hint_math_mode": "wrap math expressions in $...$",
        "log.hint_math_display": "check that the equation environment is closed",
        "log.hint_missing_open_brace": "add the missing opening {",
        "log.hint_missing_close_brace": "add the missing closing }",
        "log.hint_extra_brace": "unbalanced braces or $ — review the section",
        "log.hint_too_many_braces": "there is a } with no matching {",
        "log.hint_runaway_arg": "unclosed argument — check the {} braces",
        "log.hint_unclosed_env": "environment or { not closed before end of file",
        "log.hint_blank_in_arg": "blank line inside a command argument",
        "log.hint_missing_begin_doc": "text before \\begin{document}",
        "log.hint_usepackage_after_begin": "\\usepackage can only be used in the preamble",
        "log.hint_cmd_already_defined": "use \\renewcommand to redefine an existing command",
        "log.hint_option_clash": "same package loaded with conflicting options",
        "log.hint_env_undefined": "undefined environment — check the required \\usepackage",
        "log.hint_too_many_floats": "add \\clearpage to release accumulated figures/tables",
        "log.hint_capacity_exceeded": "TeX internal limit exceeded — simplify the document",
        "log.hint_emergency_stop": "compilation aborted — see the preceding error in the log",
        "log.hint_file_not_found": "file or package not found — check the name or install with tlmgr",
        "log.hint_no_counter": "counter referenced before being created with \\newcounter",
        "log.hint_double_subscript": "use braces: a_{bc} instead of a_b_c",
        "log.hint_double_superscript": "use braces: a^{bc} instead of a^b^c",
        "log.hint_misplaced_tab": "& used outside a table, array or align environment",
        "log.hint_extra_right": "\\right without a matching \\left",
        "log.hint_missing_delimiter": "\\left without a valid delimiter — use \\left( or \\left.",
        "log.hint_display_math": "blank line inside equation — check \\[ \\]",
        "log.hint_dimension_large": "length value too large — check the unit",
        "log.hint_arithmetic_overflow": "arithmetic overflow — simplify the expression",
        "log.hint_counter_large": "counter exceeds maximum — check lists or footnotes",
        "log.hint_missing_number": "number or length missing in argument",
        "log.hint_illegal_unit": "invalid unit — use pt, cm, mm, em, ex, etc.",
        "log.hint_bad_math_delim": "\\[ without \\] or \\( without matching \\)",
        "log.hint_verb_newline": "\\verb cannot contain a line break",
        "log.hint_caption_outside_float": "\\caption can only be used inside figure or table",
        "log.hint_missing_item": "missing \\item at the start of the list",
        "log.hint_lonely_item": "\\item outside a list environment",
        "log.hint_too_nested": "lists nested beyond 4 levels",
        "log.hint_not_outer_par": "float inside minipage, footnote or another secondary environment",
        "log.hint_nfss": "NFSS font system misconfigured — check fontenc/fontspec",
        "log.hint_cant_find_file": "file not found — check the path or name",
        "log.hint_cant_write_file": "no write permission — the PDF may be open in another program",
        "log.hint_invalid_char": "invalid character in file — check the encoding (use UTF-8)",
        "log.hint_illegal_param": "# misused — in URLs use \\#; in \\newcommand declare [N] parameters",
        "log.hint_wrong_driver": "PDF driver conflicting with hyperref + XeLaTeX",
        "log.hint_floats_lost": "float inside minipage or footnote — move it outside",
        "log.hint_bad_line_vector": "invalid argument for \\line or \\vector in picture environment",
        "log.hint_internal_bug": "TeX internal error — update your distribution or isolate the issue",
        "log.hint_font_not_found": "font not found — check exact name or install the font on your system",
        "log.hint_font_no_shape": "bold/italic/etc. variant not available for this font",
        "log.hint_font_feature": "OpenType feature not supported by this font",
        "log.hint_font_script": "OpenType script does not exist in this font",
        "log.hint_font_language": "OpenType language not available in this font",
        # build.sh
        "build.starting": "🚀 Starting build for {file} using template {template}...",
        "build.md_converted": "✅ Markdown converted to LaTeX.",
        "build.full_build": "🔧 Full build: no previous cache found.",
        "build.incremental": "⚡ Incremental build: reusing latexmk cache from previous run.",
        "build.compiling_pdf": "🔨 Compiling PDF with latexmk...",
        "build.pdf_ok": "✅ PDF generated successfully: {filename}",
        "build.pdf_error": "❌ Error: PDF was not generated.",
        "build.complete": "🎉 Process complete!",
        "build.cleaning": "🧹 Cleaning up ephemeral build files...",
        "build.warn_no_state": "⚠️ Build failed with no latexmk state — wiping cache for a clean retry.",
        "build.warn_state_kept": "⚠️ Build failed but latexmk state preserved — next run will resume incrementally.",
        "build.warn_missing_image": "⚠️ Image not found: {img} — replaced with placeholder in the document.",
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
        "uninstall.cache_removed":    "✔ Cache removed: {path}",
        "uninstall.cache_not_found":  "  Cache not found: {path}",
        "uninstall.pipx_hint":        "Run `pipx uninstall mark2tex` to remove the Python package.",
        # Clean
        "clean.removed": "✔ Cache removed: {path}",
        "clean.error":   "✗ Failed to remove cache: {path}",
        # Frontmatter validator
        "validator.parse_error": "⚠️ Could not read the YAML header. Make sure the file starts with a valid --- block.",
        "validator.missing": "⚠️ Required field missing or empty: '{field}'.",
        "validator.placeholder": "⚠️ Field '{field}' still contains the default placeholder. Fill it in before compiling.",
        "validator.template_mismatch": "⚠️ Header declares template '{fm_template}' but the TUI has '{selected}' selected. Update the header or re-select the correct template.",
        "validator.invalid_lang": "⚠️ The 'lang' value ({lang}) is not recognised. Accepted values: {accepted}.",
        "validator.warnings_header": "── YAML header warnings (compilation continues) ──",
        # Info panel (tabbed preview)
        "info.tab_markdown":   "Markdown",
        "info.tab_pdf":        "PDF Info",
        "info.pages":          "Pages generated:",
        "info.template":       "Template:",
        "info.last_compiled":  "Last compiled:",
        "info.status":         "Status:",
        "info.status_success": "Success",
        "info.status_error":   "Error",
        "info.status_pending": "Awaiting compilation",
        "info.structure":      "Document structure",
        "info.no_sections":    "No sections found.",
        "info.warnings":       "Warnings",
        "info.no_warnings":    "No warnings.",
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

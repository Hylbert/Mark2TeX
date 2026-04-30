import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CORREÇÃO PRINCIPAL: "bad escape \h at position 9"
# O LaTeX gera linhas com "\hbox", "\hspace" etc.
# Regex como re.compile("\hbox") são inválidos em Python — use raw strings:
# re.compile(r'\\hbox')  →  casa a string literal '\hbox' no texto.
# ─────────────────────────────────────────────────────────────────────────────

# Padrões compilados uma única vez (performance)
_RE_PROGRESS       = re.compile(r'^PROGRESS:(\d+)%$')
_RE_PAGE_NUMS      = re.compile(r'^(\[\d+\]\s*)+$')
_RE_OVERFULL       = re.compile(r'^(Overfull|Underfull) \\hbox \((.+?)\) in paragraph at lines (\d+)--(\d+)')
_RE_LATEX_ERROR    = re.compile(r'^! LaTeX Error: (.+)')
_RE_GENERIC_ERROR  = re.compile(r'^! (.+)')
_RE_LINE_REF       = re.compile(r'^l\.(\d+)\s*(.*)')
_RE_RUN_NUMBER     = re.compile(r"^Run number (\d+) of rule '(.+?)'")
_RE_RUNNING        = re.compile(r"^Running '(.+?)'")
_RE_RULE_CHANGE    = re.compile(r"^Rule '(.+?)': ")
_RE_LATEXMK        = re.compile(r'^Latexmk: (.+)')
_RE_DOC_CLASS      = re.compile(r'^Document Class: (\S+)')
_RE_OUTPUT_WRITTEN = re.compile(r'^Output written on (\S+) \((\d+) pages,')
_RE_PKG_WARN       = re.compile(r'^Package (\w+) Warning: (.+)')
_RE_LATEX_WARN     = re.compile(r'^LaTeX Warning: (.+)')
_RE_HOOKS_WARN     = re.compile(r'^LaTeX hooks Warning:')
_RE_MISSING_CHAR   = re.compile(r'^Missing character: There is no')
_RE_STY_PATH       = re.compile(r'^\(?/?(/usr/share/texlive|/etc/texmf|/usr/local/texlive)')
_RE_FONT_DEBUG     = re.compile(r'^(\\TU/|\\OT1/|\\T1/|\\TS1/)')
_RE_BRACKET_JUNK   = re.compile(r'^[\[\]\s]+$')
_RE_ABNT_DIVIDER   = re.compile(r'^-{30,}$')
_RE_PATH_ONLY      = re.compile(r"^\s*'?[\w./\\-]+\.(tex|aux|bbl|lof|lot|toc|log|xdv|pdf)'?\s*$")


def log_translator(line: str) -> Optional[str]:
    """
    Recebe uma linha bruta do LaTeX/latexmk (já sem o prefixo 'RAW LINE:')
    e retorna:
      - None              → suprimir (não exibir no console)
      - "__PROGRESS__N"   → atualizar progress bar para N%
      - str               → mensagem traduzida a exibir no console
    """
    stripped = line.strip()

    # Linha vazia
    if not stripped:
        return None

    # ── Diretiva PROGRESS ──────────────────────────────────────────────────
    m = _RE_PROGRESS.match(stripped)
    if m:
        return f"__PROGRESS__{m.group(1)}"

    # ── Mensagens próprias do script (emojis) — passam direto ─────────────
    first_char = stripped[0]
    if ord(first_char) > 127 and first_char not in ('(', '\\', '/'):
        return stripped

    # ── Suprimir: caminhos de pacotes .sty / .cls / etc. ──────────────────
    if _RE_STY_PATH.match(stripped):
        return None
    if stripped.startswith("/usr/share/texlive") or stripped.startswith("/etc/texmf"):
        return None

    # ── Suprimir: separadores ─────────────────────────────────────────────
    if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
        return None
    if _RE_ABNT_DIVIDER.match(stripped):
        return None

    # ── Suprimir: números de página [1] [2] [3]... ────────────────────────
    if _RE_PAGE_NUMS.match(stripped):
        return None

    # ── Suprimir: sequências de colchetes [][][]... ────────────────────────
    if _RE_BRACKET_JUNK.match(stripped) and '[' in stripped:
        return None

    # ── Suprimir: Missing character (emojis sem suporte na fonte) ─────────
    if _RE_MISSING_CHAR.match(stripped):
        return None
    if stripped.startswith('flt;mapping=tex-text;'):
        return None

    # ── Suprimir: avisos deprecated de hooks ──────────────────────────────
    if _RE_HOOKS_WARN.match(stripped):
        return None
    if stripped.startswith('(hooks)'):
        return None

    # ── Suprimir: debug interno de fontes ─────────────────────────────────
    if _RE_FONT_DEBUG.match(stripped):
        return None

    # ── Suprimir: dimensões de layout de página ───────────────────────────
    _LAYOUT_PREFIXES = (
        'Stock height', 'Top and edge', 'Page height', 'Text height',
        'Spine and edge', 'Upper and lower', 'Headheight', 'Footskip',
        'Columnsep', 'Marginparsep', 'Sidecapsep', 'Sidebarhsep',
        'Sidebarvsep', 'Sidebarheight', 'Sidefoothsep', 'Sidefootvsep',
    )
    if stripped.startswith(_LAYOUT_PREFIXES):
        return None

    # ── Suprimir: ruído pontual ────────────────────────────────────────────
    _SUPPRESS_EXACT = {
        r'\write18 enabled.',
        'entering extended mode',
        '(./output.tex',
        "Redoing nameref's sectioning",
        "Redoing nameref's label",
        'ment class',
        "For additional information on amsmath, use the `?' option.",
        'see the transcript file for additional information',
        'Transcript written on output.log.',
        'bibitemlist',
        'output.aux', 'output.lof', 'output.lot', 'output.toc',
        'TeX engine is XeTeX',
    }
    if stripped in _SUPPRESS_EXACT:
        return None

    _SUPPRESS_PREFIX = (
        'L3 programming layer',
        'LaTeX2e <',
        '(|extractbb',
        'Package hyperref Warning: Rerun',
        'Package hyperref Warning: Suppressing empty link',
        'Changed files, or newly in use',
        'The top-level auxiliary file',
        'Em caso de dúvidas',
        'http://www.abntex',
        'See the LaTeX manual',
        'Type  H <return>',
    )
    if stripped.startswith(_SUPPRESS_PREFIX):
        return None

    # Suprimir linhas que são só paths avulsos (output.aux, etc.)
    if _RE_PATH_ONLY.match(stripped):
        return None

    # Suprimir continuações numéricas soltas: [2.5cm], [9cm]
    if re.match(r'^\[\d+(\.\d+)?[a-z]*\]$', stripped):
        return None

    # ── Rc files read ──────────────────────────────────────────────────────
    if stripped == 'Rc files read:':
        return '⚙️ Config: lendo arquivos de configuração'
    if re.match(r'^/etc/[Ll]atex', stripped):
        return f'⚙️ Config: {stripped}'

    # ── Output written ─────────────────────────────────────────────────────
    m = _RE_OUTPUT_WRITTEN.match(stripped)
    if m:
        fmt, pages = m.group(1), m.group(2)
        return f'📄 Saída gerada: {fmt} ({pages} páginas)'

    # ── Latexmk mensagens ──────────────────────────────────────────────────
    m = _RE_LATEXMK.match(stripped)
    if m:
        msg = m.group(1).strip()
        if msg.startswith('applying rule'):
            rule = re.search(r"'(.+?)'", msg)
            name = rule.group(1) if rule else msg
            return f'🔧 Aplicando regra: {name}'
        if 'This is Latexmk' in msg:
            ver = re.search(r'version: ([\d.]+)', msg)
            v = ver.group(1) if ver else ''
            return f'ℹ️ Latexmk {v}'
        if 'References changed' in msg:
            return '🔄 Referências alteradas, recompilando...'
        if 'Found bibliography files' in msg:
            f_match = re.search(r'files (.+)$', msg)
            fname = f_match.group(1) if f_match else msg
            return f'📚 Arquivo de referências: {fname}'
        if 'Found input bbl' in msg or 'Log file says' in msg or 'Examining' in msg:
            return None
        return f'🔧 Latexmk: {msg}'

    # ── This is XeTeX / BibTeX ─────────────────────────────────────────────
    if stripped.startswith('This is XeTeX'):
        ver = re.search(r'Version ([\d.\-]+)', stripped)
        v = ver.group(1) if ver else ''
        return f'ℹ️ Motor: XeTeX {v}'
    if stripped.startswith('This is BibTeX'):
        ver = re.search(r'Version ([\d.]+)', stripped)
        v = ver.group(1) if ver else ''
        return f'ℹ️ Motor: BibTeX {v}'

    # ── Document Class ─────────────────────────────────────────────────────
    m = _RE_DOC_CLASS.match(stripped)
    if m:
        cls = m.group(1)
        if cls == 'memoir':
            return None  # classe interna
        ver = re.search(r'v[-\d.]+', stripped)
        v = f' {ver.group(0)}' if ver else ''
        return f'📄 Classe: {cls}{v}'

    # ── Rule / Run ─────────────────────────────────────────────────────────
    if _RE_RULE_CHANGE.match(stripped):
        return None  # "Rule 'xelatex': File changes..." → suprimir

    m = _RE_RUN_NUMBER.match(stripped)
    if m:
        n, rule = m.group(1), m.group(2)
        return f'🔄 Compilação {n} — regra: {rule}'

    m = _RE_RUNNING.match(stripped)
    if m:
        cmd = m.group(1)
        if 'xelatex' in cmd:
            return '▶️ xelatex output.tex'
        if 'bibtex' in cmd:
            parts = cmd.split()
            arg = parts[-1] if parts else ''
            return f'▶️ bibtex {arg}'
        return f'▶️ {cmd[:80]}'

    # ── Erros LaTeX ────────────────────────────────────────────────────────
    m = _RE_LATEX_ERROR.match(stripped)
    if m:
        return f'❌ Erro LaTeX: {m.group(1)}'

    m = _RE_GENERIC_ERROR.match(stripped)
    if m:
        return f'❌ {m.group(1)}'

    # ── Localização do erro: l.XX ──────────────────────────────────────────
    m = _RE_LINE_REF.match(stripped)
    if m:
        lineno, ctx = m.group(1), m.group(2).strip()
        # Limpar contexto de debug de fonte TeX
        ctx = re.sub(r'\\TU/\S+\s*', '', ctx).strip()
        if ctx:
            return f'   ↳ linha {lineno}: {ctx}'
        return f'   ↳ linha {lineno}'

    # ── Overfull / Underfull hbox ──────────────────────────────────────────
    # CORREÇÃO: r'\\hbox' em vez de '\hbox' (evita "bad escape \h")
    m = _RE_OVERFULL.match(stripped)
    if m:
        kind, amount, l1, l2 = m.groups()
        if kind == 'Underfull':
            return None  # underfull é cosmético
        # Só mostrar overfull significativo (> 5pt)
        pts_match = re.search(r'[\d.]+', amount)
        if pts_match:
            try:
                if float(pts_match.group()) < 5.0:
                    return None
            except ValueError:
                pass
        return f'⚠️ Texto largo ({amount}) nas linhas {l1}–{l2}'

    # ── Avisos de pacotes ──────────────────────────────────────────────────
    m = _RE_PKG_WARN.match(stripped)
    if m:
        pkg, msg = m.group(1), m.group(2)
        if 'Suppressing empty link' in msg or 'Rerun' in msg:
            return None
        return f'⚠️ [{pkg}] {msg}'

    m = _RE_LATEX_WARN.match(stripped)
    if m:
        msg = m.group(1)
        if 'Labels may have changed' in msg:
            return '🔄 Referências alteradas, recompilando...'
        if 'Empty thebibliography' in msg:
            return '⚠️ Seção de referências vazia'
        if 'Rerun' in msg:
            return None
        return f'⚠️ {msg}'

    # ── BibTeX ─────────────────────────────────────────────────────────────
    if stripped.startswith('The style file'):
        sty = stripped.replace('The style file', '').strip()
        return f'📝 Estilo bibliográfico: {sty}'
    if stripped.startswith('Database file'):
        db = re.sub(r'^Database file\s*#?\d*:?\s*', '', stripped)
        return f'📚 Base de dados: {db}'
    if 'I found no commands' in stripped:
        return 'ℹ️ Nenhuma citação encontrada no documento'
    if re.match(r'^There was[e]? \d+ error', stripped):
        return f'❌ {stripped}'

    # ── Suprimir: linhas muito curtas ou só pontuação ──────────────────────
    if len(stripped) <= 2:
        return None
    if re.match(r'^[()./\\]+$', stripped):
        return None

    # ── Passagem direta para o restante ────────────────────────────────────
    return stripped
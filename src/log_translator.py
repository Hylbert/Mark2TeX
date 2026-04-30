import re

class LogTranslator:
    """
    Translates raw LaTeX/Pandoc error logs into human-friendly messages.
    """

    # Mapping of regex patterns to human-friendly messages
    # Order matters: more specific patterns should come first
    TRANSLATIONS = [
        (
            r"PROGRESS:(\d+)%",
            lambda m: f"⏳ Processing... {m.group(1)}%"
        ),
        # --- Silêncio (linhas que devem ser completamente ignoradas) ---
        (
            r"Missing character:.*",
            None
        ),
        (
            r"flt;mapping=.*",
            None
        ),
        (
            r"Overfull \\hbox.*",
            None
        ),
        (
            r"Latexmk: This is Latexmk.*",
            None
        ),
        (
            r"Latexmk:*",
            None
        ),
        (
            r"Rule '.*'.*",
            None
        ),
        (
            r"Package hyperref Warning*",
            None
        ),
        (
            r"\\write18 enabled",
            None
        ),
        # Filtro para números de página [46] ou sequências [48] [49]

        (
            r"\[\d+\]",
            None
        ),
        # Filtro para sequências de colchetes vazios [][][][]
        (
            r"\[\]",
            None
        ),
        # Filtro para caminhos de arquivos (/usr/share/...sty)
        (
            r"\(.*?\)",
            None
        ),
        # Filtro para linhas vazias ou apenas com espaços
        (
            r"^\s*$",
            None
        ),
        # --- Mensagens Humanas ---
        (
            r"Stock height and width:.*",
            "📏 Layout: Stock height and width"
        ),
        (
            r"Top and edge trims:.*",
            "📏 Layout: Top and edge trims"
        ),
        (
            r"Page height and width:.*",
            "📏 Layout: Page height and width"
        ),
        (
            r"Rc files read:.*",
            "⚙️ Config: Rc files read"
        ),
        (
            r"! LaTeX Error: File '.*\.tex' not found",
            "❌ Erro: Arquivo de template não encontrado. Verifique se o template existe em ~/.mark2tex/templates."
        ),
        (
            r"See the LaTeX*",
            None
        ),
        (
            r"! LaTeX Error: There's no line here to end",
            None
        ),
        (
            r"Type  H *",
            None
        ),
        (
            r"LaTeX *",
            None
        ),
        (
            r"Undefined control sequence",
            "⚠️ Aviso: Comando LaTeX desconhecido encontrado. Verifique a sintaxe do seu documento."
        ),
        (
            r"BibTeX Error",
            "📚 Erro: Problema na bibliografia. Verifique o arquivo referencias.bib."
        ),
        (
            r"Missing \$ inserted",
            "⚠️ Aviso: Falta um símbolo de cifrão ($) para fechar o modo matemático."
        ),
        (
            r"Emergency stop",
            "🚨 Erro Crítico: O compilador LaTeX parou inesperadamente. Verifique os erros acima."
        ),
        (
            r"Can't find .* on the system",
            "❌ Erro: Recurso do sistema não encontrado. Pode ser necessário instalar pacotes adicionais no Docker."
        ),
    ]

    @classmethod
    def translate(cls, line: str) -> str:
        """
        Processes a line of log output and returns the translated version if a match is found.
        Returns None if the line should be completely hidden.
        """
        for pattern, message in cls.TRANSLATIONS:
            if re.search(pattern, line):
                if message is None:
                    return None

                # Se a mensagem for uma função (lambda), executamos ela passando o match
                if callable(message):
                    result = message(re.search(pattern, line))
                else:
                    result = message

                return result

        return line

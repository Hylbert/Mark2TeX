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
        (
            r"Stock height and width:.*",
            "📏 Layout: Stock height and width" # Show minimal info
        ),
        (
            r"Top and edge trims:.*",
            "📏 Layout: Top and edge trims" # Show minimal info
        ),
        (
            r"Page height and width:.*",
            "📏 Layout: Page height and width" # Show minimal info
        ),
        (
            r"Rc files read:.*",
            "⚙️ Config: Rc files read" # Show minimal info
        ),
        (
            r"! LaTeX Error: File '.*\.tex' not found",
            "❌ Erro: Arquivo de template não encontrado. Verifique se o template existe em ~/.mark2tex/templates."
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

                return f"{result}\n(Original: {line.strip()})"

        return line

import re

class LogTranslator:
    """
    Translates raw LaTeX/Pandoc error logs into human-friendly messages.
    """

    # Mapping of regex patterns to human-friendly messages
    # Order matters: more specific patterns should come first
    TRANSLATIONS = [
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
        """
        for pattern, message in cls.TRANSLATIONS:
            if re.search(pattern, line):
                return f"{message}\n(Original: {line.strip()})"

        return line

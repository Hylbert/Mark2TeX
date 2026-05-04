#!/bin/bash

# Verifica se o arquivo de entrada foi fornecido
if [ -z "$1" ]; then
    echo "❌ Erro: Você deve fornecer o arquivo .md de entrada."
    echo "Uso: ./watch.sh <arquivo.md> [template]"
    echo "Exemplo: ./watch.sh meu_tcc.md tcc"
    exit 1
fi

INPUT_FILE="$1"
TEMPLATE="${2:-tcc}" # Usa 'tcc' como padrão se o segundo argumento estiver vazio

# Verifica se o arquivo existe
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Erro: Arquivo '$INPUT_FILE' não encontrado."
    exit 1
fi

echo "👀 Monitoring $INPUT_FILE using template '$TEMPLATE' for changes..."
echo "Press Ctrl+C to stop."

# Pega o timestamp inicial do arquivo
LAST_MOD=$(stat -c %Y "$INPUT_FILE")

while true; do
    # Verifica o timestamp atual
    CURRENT_MOD=$(stat -c %Y "$INPUT_FILE")

    if [ "$CURRENT_MOD" != "$LAST_MOD" ]; then
        echo "📝 Change detected at $(date +%H:%M:%S). Compiling..."
        make compile INPUT="$INPUT_FILE" TEMPLATE="$TEMPLATE"

        if [ $? -eq 0 ]; then
            echo "✨ PDF updated successfully!"
        else
            echo "❌ Compilation failed. Check output.log"
        fi

        LAST_MOD=$CURRENT_MOD
    fi

    # Espera 2 segundos antes de checar novamente
    sleep 2
done

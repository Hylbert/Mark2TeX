#!/bin/bash
set -e

# Inputs from arguments
INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
OUTPUT_NAME="output"

# --- SECURITY VALIDATION ---

# 1. Validate INPUT_FILE: Must not be empty and must end with .md
if [[ -z "$INPUT_FILE" ]]; then
    echo "❌ Error: Input file is required."
    echo "Usage: $0 <file.md> <template>"
    exit 1
fi

if [[ "$INPUT_FILE" != *.md ]]; then
    echo "❌ Error: Input file must have a .md extension."
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "❌ Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

# 2. Validate TEMPLATE_TYPE: Must be in the allowed whitelist
ALLOWED_TEMPLATES=("tcc" "artigo" "projeto")
IS_VALID=false

for t in "${ALLOWED_TEMPLATES[@]}"; do
    if [[ "$TEMPLATE_TYPE" == "$t" ]]; then
        IS_VALID=true
        break
    fi
done

if [[ "$IS_VALID" == "false" ]]; then
    echo "❌ Error: Invalid template '$TEMPLATE_TYPE'."
    echo "Allowed templates are: ${ALLOWED_TEMPLATES[*]}"
    exit 1
fi

# --- END SECURITY VALIDATION ---

echo "🚀 Starting build for $INPUT_FILE using template $TEMPLATE_TYPE..."

# 1. Pandoc Conversion to LaTeX
# Use double quotes to prevent command injection via variables
pandoc "$INPUT_FILE" \
    --template="templates/$TEMPLATE_TYPE/template.tex" \
    --pdf-engine=xelatex \
    --bibliography=referencias.bib \
    --citeproc \
    --wrap=preserve \
    --listings \
    -o "$OUTPUT_NAME.tex"

echo "✅ Markdown converted to LaTeX."

# 2. LaTeX Compilation
echo "🔨 Compiling PDF with latexmk..."
latexmk -pdfxe -f -interaction=nonstopmode -shell-escape -bibtex "$OUTPUT_NAME.tex"

echo "✅ PDF generated successfully."

# 3. Cleanup
echo "🧹 Cleaning up auxiliary files..."
rm -f *.aux *.log *.out *.toc *.lot *.lof *.bbl *.blg *.synctex.gz

echo "🎉 Process complete! Final file: $OUTPUT_NAME.pdf"

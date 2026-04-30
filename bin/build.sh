#!/bin/bash
export PYTHONUNBUFFERED=1
# set -e  # Removed to allow compilation to continue despite LaTeX warnings
# set -x # Removed to clean up console output

# Inputs from arguments
INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
OUTPUT_NAME="output"

# --- SECURITY VALIDATION ---

# 1. Validate INPUT_FILE
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

# 2. Validate TEMPLATE_TYPE
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
echo "PROGRESS:10%"
sync

# Define cleanup function to be called on exit
cleanup() {
    echo "🧹 Cleaning up auxiliary files..."
    # Only remove logs and aux files related to the output name to avoid deleting tui_debug.log
    rm -f "$OUTPUT_NAME".aux "$OUTPUT_NAME".log "$OUTPUT_NAME".out "$OUTPUT_NAME".toc "$OUTPUT_NAME".lot "$OUTPUT_NAME".lof "$OUTPUT_NAME".bbl "$OUTPUT_NAME".blg "$OUTPUT_NAME".synctex.gz "$OUTPUT_NAME".fls "$OUTPUT_NAME".fdb_latexmk "$OUTPUT_NAME".xdv "$OUTPUT_NAME".tex || true
}

# The trap ensures cleanup() runs regardless of whether the script succeeds or fails
trap cleanup EXIT

echo "🚀 Starting build for $INPUT_FILE using template $TEMPLATE_TYPE..."

# 1. Pandoc Conversion to LaTeX
BIB_ARGS=""
if [[ -f "referencias.bib" ]]; then
    BIB_ARGS="--bibliography=referencias.bib --citeproc"
fi

TEMPLATE_PATH="/app/templates/$TEMPLATE_TYPE/template.tex"

pandoc "$INPUT_FILE" \
    --template="$TEMPLATE_PATH" \
    --pdf-engine=xelatex \
    $BIB_ARGS \
    --wrap=preserve \
    --listings \
    -o "$OUTPUT_NAME.tex"

echo "✅ Markdown converted to LaTeX."
echo "PROGRESS:40%"
sync

# 2. LaTeX Compilation
echo "🔨 Compiling PDF with latexmk..."
echo "PROGRESS:50%"
sync
latexmk -pdfxe -f -interaction=nonstopmode -shell-escape -bibtex "$OUTPUT_NAME.tex"

if [[ -f "$OUTPUT_NAME.pdf" ]]; then
    echo "✅ PDF generated successfully: $OUTPUT_NAME.pdf"
    echo "PROGRESS:100%"
    sync
else
    echo "❌ Error: PDF was not generated."
    exit 1
fi

echo "🎉 Process complete!"

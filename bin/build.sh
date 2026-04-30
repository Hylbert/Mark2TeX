#!/bin/bash
export PYTHONUNBUFFERED=1

INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
OUTPUT_NAME="${INPUT_FILE%.*}"
TEMPLATE_BASE="${MARK2TEX_TEMPLATE_DIR:-/app/templates}"

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

echo "PROGRESS:10%"
sync

cleanup() {
    echo "🧹 Cleaning up auxiliary files..."
    rm -f "$OUTPUT_NAME".aux "$OUTPUT_NAME".log "$OUTPUT_NAME".out "$OUTPUT_NAME".toc \
          "$OUTPUT_NAME".lot "$OUTPUT_NAME".lof "$OUTPUT_NAME".bbl "$OUTPUT_NAME".blg \
          "$OUTPUT_NAME".synctex.gz "$OUTPUT_NAME".fls "$OUTPUT_NAME".fdb_latexmk \
          "$OUTPUT_NAME".xdv "$OUTPUT_NAME".tex || true
}
trap cleanup EXIT

echo "🚀 Starting build for $INPUT_FILE using template $TEMPLATE_TYPE..."

BIB_ARGS=""
if [[ -f "referencias.bib" ]]; then
    BIB_ARGS="--bibliography=referencias.bib --citeproc"
fi

TEMPLATE_PATH="$TEMPLATE_BASE/$TEMPLATE_TYPE/template.tex"

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

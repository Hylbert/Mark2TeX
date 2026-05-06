#!/bin/bash
export PYTHONUNBUFFERED=1

INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
FONT_VALUE=""
OUTPUT_NAME="${INPUT_FILE%.*}"
TEMPLATE_BASE="${MARK2TEX_TEMPLATE_DIR:-/app/templates}"

# Cache dir for latexmk intermediate files (persistent across runs)
CACHE_DIR="${OUTPUT_NAME}.m2t-cache"

# Parse optional --font <value> argument
shift 2
while [[ $# -gt 0 ]]; do
    case "$1" in
        --font)
            FONT_VALUE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [[ -z "$INPUT_FILE" ]]; then
    echo "❌ Error: Input file is required."
    echo "Usage: $0 <file.md> <template> [--font <font>]"
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

# Discover valid templates dynamically
ALLOWED_TEMPLATES=()
while IFS= read -r -d '' dir; do
    name=$(basename "$dir")
    if [[ -f "$dir/template.tex" ]]; then
        ALLOWED_TEMPLATES+=("$name")
    fi
done < <(find "$TEMPLATE_BASE" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

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

# ---------------------------------------------------------------------------
# Cleanup: remove only ephemeral per-run files.
# The cache dir is intentionally kept for incremental reuse.
# If latexmk failed AND no PDF was produced, wipe the cache so the
# next run starts clean rather than re-failing on a corrupted graph.
# ---------------------------------------------------------------------------
cleanup() {
    local exit_code=$?
    echo "🧹 Cleaning up ephemeral build files..."
    rm -f "$OUTPUT_NAME".tex "$OUTPUT_NAME".xdv || true
    # latexmk writes a copy of the PDF inside the cache dir when -outdir
    # differs from -auxdir; remove it to avoid confusion.
    rm -f "${CACHE_DIR}/${OUTPUT_NAME##*/}.pdf" || true
    if [[ $exit_code -ne 0 && ! -f "$OUTPUT_NAME.pdf" ]]; then
        echo "⚠️  Build failed — wiping cache for next run."
        rm -rf "$CACHE_DIR" || true
    fi
}
trap cleanup EXIT

echo "🚀 Starting build for $INPUT_FILE using template $TEMPLATE_TYPE..."

BIB_ARGS=""
if [[ -f "referencias.bib" ]]; then
    BIB_ARGS="--bibliography=referencias.bib --citeproc"
fi

# Convert --font to boolean metadata flags for Pandoc.
# Pandoc does NOT support string comparison in templates.
FONT_ARGS=""
case "$FONT_VALUE" in
    arial)     FONT_ARGS="--metadata=font-arial:true" ;;
    helvetica) FONT_ARGS="--metadata=font-helvetica:true" ;;
    ubuntu)    FONT_ARGS="--metadata=font-ubuntu:true" ;;
    times)     FONT_ARGS="--metadata=font-times:true" ;;
esac

TEMPLATE_PATH="$TEMPLATE_BASE/$TEMPLATE_TYPE/template.tex"

pandoc "$INPUT_FILE" \
    --template="$TEMPLATE_PATH" \
    --pdf-engine=xelatex \
    $BIB_ARGS \
    $FONT_ARGS \
    --wrap=preserve \
    --listings \
    -o "$OUTPUT_NAME.tex"

echo "✅ Markdown converted to LaTeX."
echo "PROGRESS:40%"
sync

# ---------------------------------------------------------------------------
# Incremental compilation
# -auxdir  keeps all intermediate files (.aux, .fdb_latexmk, .fls, ...)
#          in the cache dir so they survive between runs.
# -outdir  places the final PDF next to the source .md file as before.
# mkdir -p ensures the cache dir exists on first run.
# ---------------------------------------------------------------------------
mkdir -p "$CACHE_DIR"

if [[ -f "${CACHE_DIR}/$(basename "$OUTPUT_NAME").fdb_latexmk" ]]; then
    echo "⚡ Incremental build: reusing latexmk cache from previous run."
else
    echo "🔧 Full build: no previous cache found."
fi

echo "🔨 Compiling PDF with latexmk..."
echo "PROGRESS:50%"
sync

latexmk \
    -pdfxe \
    -f \
    -interaction=nonstopmode \
    -shell-escape \
    -bibtex \
    -auxdir="$CACHE_DIR" \
    -outdir="/app" \
    "$OUTPUT_NAME.tex"

if [[ -f "$OUTPUT_NAME.pdf" ]]; then
    echo "✅ PDF generated successfully: $OUTPUT_NAME.pdf"
    echo "PROGRESS:100%"
    sync
else
    echo "❌ Error: PDF was not generated."
    exit 1
fi

echo "🎉 Process complete!"

#!/bin/bash
export PYTHONUNBUFFERED=1

INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
FONT_VALUE=""
OUTPUT_NAME="${INPUT_FILE%.*}"
TEMPLATE_BASE="${MARK2TEX_TEMPLATE_DIR:-/app/templates}"

# Cache dir for latexmk intermediate files.
# Provided by docker_manager.py as M2T_CACHE_DIR (mounted at /m2t-cache).
# Falls back to /tmp/m2t-cache if run outside Docker.
CACHE_DIR="${M2T_CACHE_DIR:-/tmp/m2t-cache}"

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
# Cleanup: remove only ephemeral per-run files from the working directory.
#
# Rules:
#   SUCCESS  — remove .tex and .xdv from /app; leave the cache dir intact
#              so latexmk can do a real incremental build next time.
#   FAILURE  — remove .tex and .xdv from /app; wipe the cache ONLY when
#              the .fdb_latexmk file is missing, meaning latexmk never
#              completed a full pass and the cache may be corrupted.
#              If .fdb_latexmk exists the partial cache is still useful
#              (latexmk will pick up where it left off).
# ---------------------------------------------------------------------------
cleanup() {
    local exit_code=$?
    local doc_stem
    doc_stem="$(basename "$OUTPUT_NAME")"

    echo "🧹 Cleaning up ephemeral build files..."
    # Remove intermediate .tex/.xdv from the working dir (not the cache).
    rm -f "$OUTPUT_NAME".tex "$OUTPUT_NAME".xdv || true
    # latexmk writes an extra PDF inside the cache dir when -outdir differs
    # from -auxdir; remove it to avoid confusion with the real output.
    rm -f "${CACHE_DIR}/${doc_stem}.pdf" || true

    if [[ $exit_code -ne 0 && ! -f "${OUTPUT_NAME}.pdf" ]]; then
        if [[ ! -f "${CACHE_DIR}/${doc_stem}.fdb_latexmk" ]]; then
            echo "⚠️  Build failed with no latexmk state — wiping cache for a clean retry."
            rm -rf "${CACHE_DIR:?}"/* || true
        else
            echo "⚠️  Build failed but latexmk state preserved — next run will resume incrementally."
        fi
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
# -auxdir  keeps intermediate files in the host-mounted cache dir so they
#          survive between container runs (container is --rm).
# -outdir  places the final PDF next to the source .md file (unchanged).
# ---------------------------------------------------------------------------
mkdir -p "$CACHE_DIR"

DOC_STEM="$(basename "$OUTPUT_NAME")"
if [[ -f "${CACHE_DIR}/${DOC_STEM}.fdb_latexmk" ]]; then
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

if [[ -f "${OUTPUT_NAME}.pdf" ]]; then
    echo "✅ PDF generated successfully: ${OUTPUT_NAME}.pdf"
    echo "PROGRESS:100%"
    sync
else
    echo "❌ Error: PDF was not generated."
    exit 1
fi

echo "🎉 Process complete!"

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
# SUCCESS: remove .tex and .fls from /app; leave the cache dir intact so
#          latexmk can do a real incremental build next time.
# FAILURE: remove .tex and .fls from /app; wipe the cache ONLY when
#          .fdb_latexmk is missing (latexmk never completed a full pass).
#          If .fdb_latexmk exists, preserve it so the next run resumes.
#
# Note on .fls: latexmk always writes the file list (.fls) to $out_dir
# (/app) at the end of every run, even when $fls_file is set in .latexmkrc
# (it moves the file back during finalisation). The .fls is not required
# for incremental builds — latexmk uses .fdb_latexmk for that — so it is
# safe to delete it unconditionally after each compilation.
# ---------------------------------------------------------------------------
cleanup() {
    local exit_code=$?
    local doc_stem
    doc_stem="$(basename "$OUTPUT_NAME")"

    echo "🧹 Cleaning up ephemeral build files..."
    rm -f "$OUTPUT_NAME".tex || true
    rm -f "$OUTPUT_NAME".fls || true
    # Remove any stray PDF that xdvipdfmx may write inside the cache dir.
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

# Only pass --bibliography to pandoc if the source .md actually contains
# citations ([@key] Pandoc syntax or \cite{key} LaTeX syntax).
# Passing --bibliography unconditionally causes pandoc to emit \bibliography{}
# in the .tex, which makes latexmk always schedule bibtex — even with -bibtex-
# — leading to a 'Missing bbl / missing \item' loop on citation-free docs.
BIB_ARGS=""
if [[ -f "referencias.bib" ]] && grep -qE '\[@[^]]+\]|\\cite\{' "$INPUT_FILE" 2>/dev/null; then
    BIB_ARGS="--bibliography=referencias.bib --citeproc"
fi

# Convert --font to boolean metadata flags for Pandoc.
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
# Incremental compilation — TeX Live / latexmk 4.76 compatible
#
# latexmk 4.76 (Ubuntu 22.04 / TeX Live 2022) has a known issue:
# even when $aux_dir is set in .latexmkrc, it still passes -aux-directory
# to xelatex on the first invocation before detecting that xelatex does
# not support that flag and falling back to emulate_aux mode.
#
# Fix: set $emulate_aux = 1 explicitly. latexmk then uses its own
# copy-based emulation from the very first pass, never passing
# -aux-directory or -output-directory to xelatex. All intermediates
# (.aux, .log, .bbl, .xdv) are kept in $aux_dir via copy, and the
# final PDF goes to $out_dir=/app.
# ---------------------------------------------------------------------------
mkdir -p "$CACHE_DIR"

DOC_STEM="$(basename "$OUTPUT_NAME")"

# Write (or refresh) the per-document latexmkrc inside the cache dir.
LATEXMKRC="${CACHE_DIR}/.latexmkrc"
cat > "$LATEXMKRC" << RCEOF
# Auto-generated by mark2tex build.sh — do not edit manually.
\$emulate_aux = 1;
\$aux_dir = '${CACHE_DIR}';
\$out_dir = '/app';
RCEOF

if [[ -f "${CACHE_DIR}/${DOC_STEM}.fdb_latexmk" ]]; then
    echo "⚡ Incremental build: reusing latexmk cache from previous run."
else
    echo "🔧 Full build: no previous cache found."
fi

echo "🔨 Compiling PDF with latexmk..."
echo "PROGRESS:50%"
sync

# ---------------------------------------------------------------------------
# Granular progress during latexmk
#
# latexmk reports each XeLaTeX pass with a line like:
#   "Run number N of rule 'xelatex'"
# We pipe its combined output (stdout + stderr) through a while-read loop
# that intercepts those markers and emits PROGRESS tokens so the TUI bar
# advances in real time instead of jumping from 50% to 100% after a long
# silence on large documents.
#
# Pass mapping (conservative — most documents need 2–3 passes):
#   Run 1 starts   → 60%   (first xelatex pass begun)
#   Run 2 starts   → 75%   (cross-references / TOC pass)
#   Run 3 starts   → 88%   (final stabilisation pass)
#   xdvipdfmx pass → 94%   (PDF assembly from .xdv)
#
# Exit-code recovery: bash pipes run the right-hand side in a subshell, so
# $? after a pipe reflects the last command in the pipe (the while loop),
# not latexmk itself. We use a temp file inside CACHE_DIR to persist the
# real latexmk exit code across the subshell boundary.
#
# -bibtex- unconditionally disables bibtex in latexmk.
# Citation-free docs never emit \bibliography{} (guarded above), so latexmk
# has no reason to schedule bibtex regardless. When citations are present,
# pandoc's --citeproc resolves them at the Markdown→LaTeX step, so bibtex
# is also not needed at the latexmk level.
# ---------------------------------------------------------------------------
LATEXMK_EXIT_FILE="${CACHE_DIR}/.latexmk_exit"

# Run latexmk in a subshell so we can capture its exit code separately,
# then pipe to the progress-emitting reader loop.
(
    latexmk \
        -pdfxe \
        -f \
        -interaction=nonstopmode \
        -shell-escape \
        -bibtex- \
        -r "$LATEXMKRC" \
        "$OUTPUT_NAME.tex"
    echo $? > "$LATEXMK_EXIT_FILE"
) 2>&1 | while IFS= read -r line; do
    echo "$line"
    case "$line" in
        *"Run number 1 of rule"*xelatex*)
            echo "PROGRESS:60%" ; sync ;;
        *"Run number 2 of rule"*xelatex*)
            echo "PROGRESS:75%" ; sync ;;
        *"Run number 3 of rule"*xelatex*)
            echo "PROGRESS:88%" ; sync ;;
        *"Run number"*"of rule"*xdvipdfmx*|*"Running 'xdvipdfmx"*)
            echo "PROGRESS:94%" ; sync ;;
    esac
done

# Read back the real latexmk exit code written by the subshell above.
LATEXMK_EXIT=$(cat "$LATEXMK_EXIT_FILE" 2>/dev/null || echo 1)
rm -f "$LATEXMK_EXIT_FILE"

if [[ "$LATEXMK_EXIT" -ne 0 ]]; then
    # latexmk failed — let the cleanup trap handle cache wiping.
    exit "$LATEXMK_EXIT"
fi

if [[ -f "${OUTPUT_NAME}.pdf" ]]; then
    echo "✅ PDF generated successfully: ${OUTPUT_NAME}.pdf"
    echo "PROGRESS:100%"
    sync
else
    echo "❌ Error: PDF was not generated."
    exit 1
fi

echo "🎉 Process complete!"

#!/bin/bash
export PYTHONUNBUFFERED=1

INPUT_FILE="$1"
TEMPLATE_TYPE="$2"
FONT_VALUE=""
OUTPUT_NAME="${INPUT_FILE%.*}"

# Templates are mounted from the host package directory at runtime
# (bind mount to /opt/mark2tex/templates). MARK2TEX_TEMPLATE_DIR is set
# by docker_manager.py to that path. The fallback /opt/mark2tex/templates
# matches the Dockerfile COPY destination for use outside Docker.
TEMPLATE_BASE="${MARK2TEX_TEMPLATE_DIR:-/opt/mark2tex/templates}"

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
    # Remove the pre-processed markdown copy if it exists.
    rm -f "${OUTPUT_NAME}._processed.md" || true
    # Remove any stray PDF that xdvipdfmx may write inside the cache dir.
    rm -f "${CACHE_DIR}/${doc_stem}.pdf" || true
    # Remove SyncTeX file from the output dir ($out_dir=/app).
    # xelatex writes it to the output directory, not the cache, so the cache
    # cleanup above does not catch it.  -synctex=0 in latexmkrc prevents
    # generation; this rm is a safety net for older cache entries.
    rm -f "$OUTPUT_NAME".synctex.gz || true

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

# ---------------------------------------------------------------------------
# Pre-check: scan for local image references and replace missing ones with
# a plain-text placeholder so XeLaTeX can compile the full document instead
# of producing an empty/0-page PDF.
#
# Remote URLs (http/https) are skipped — they pass straight through to
# \includegraphics and are handled by the LaTeX run itself.
# ---------------------------------------------------------------------------
MISSING_IMAGES=()
PROCESSED_INPUT="${OUTPUT_NAME}._processed.md"
cp "$INPUT_FILE" "$PROCESSED_INPUT"

while IFS= read -r img_path; do
    [[ "$img_path" =~ ^https?:// ]] && continue
    if [[ ! -f "$img_path" ]]; then
        MISSING_IMAGES+=("$img_path")
        # Escape special regex characters in the path for sed.
        escaped_path=$(printf '%s' "$img_path" | sed 's/[\[\]\\.*^$(){}+?|]/\\&/g')
        # Replace every ![alt](path) that uses this missing path with a
        # visible plain-text marker.  The replacement text is safe for both
        # Markdown and the LaTeX that pandoc generates from it.
        sed -i "s|!\[[^]]*\](${escaped_path})|[IMAGE NOT FOUND: ${img_path}]|g" "$PROCESSED_INPUT"
    fi
done < <(grep -oP '!\[[^\]]*\]\(\K[^)]+' "$INPUT_FILE")

for img in "${MISSING_IMAGES[@]}"; do
    echo "⚠️ MISSING_IMAGE:${img}"
done

# ---------------------------------------------------------------------------
# Smart heading numbering: if the user already wrote an explicit numeric
# prefix in a Markdown heading (e.g. `# 1 Introduction`, `## 1.1 Background`,
# `### 1.1.1 Details`), strip that prefix before passing to pandoc.
# This prevents LaTeX from duplicating the number that the auto-counter
# would add (e.g. avoiding `1 1 Introduction` in the PDF).
#
# Patterns matched and stripped (YAML frontmatter is left untouched):
#   # N Title          →  # Title
#   ## N.N Title       →  ## Title
#   ### N.N.N Title    →  ### Title
#
# Headings without a leading numeric prefix are left completely unchanged.
#
# Set `preserve-heading-numbers: true` in the document's YAML frontmatter
# to opt out of stripping — useful when LaTeX auto-numbering is disabled
# and the numeric prefixes are intentional (e.g. form section numbers).
# ---------------------------------------------------------------------------
PRESERVE_NUMBERS=$(grep -m1 '^preserve-heading-numbers:' "$INPUT_FILE" | \
    sed 's/^preserve-heading-numbers:[[:space:]]*//' | tr -d '"'"'" | tr -d '[:space:]')

if [[ "$PRESERVE_NUMBERS" != "true" ]]; then
    sed -i \
        -e 's/^\(# \)\([0-9]\+\. \+\)/\1/' \
        -e 's/^\(## \)\([0-9]\+\.[0-9]\+\. \+\)/\1/' \
        -e 's/^\(### \)\([0-9]\+\.[0-9]\+\.[0-9]\+\. \+\)/\1/' \
        -e 's/^\(# \)\([0-9]\+ \+\)/\1/' \
        -e 's/^\(## \)\([0-9]\+\.[0-9]\+ \+\)/\1/' \
        -e 's/^\(### \)\([0-9]\+\.[0-9]\+\.[0-9]\+ \+\)/\1/' \
        "$PROCESSED_INPUT"
fi

# Hand the (possibly modified) copy to pandoc.
INPUT_FILE="$PROCESSED_INPUT"

# ---------------------------------------------------------------------------
# Bibliography resolution
#
# Read the `bibliography` field directly from the YAML frontmatter of the
# source .md file. If the field is present and the corresponding .bib file
# exists on disk, pass --bibliography to Pandoc so it populates the
# $bibliography$ template variable — which in turn triggers the
# \bibliographystyle + \bibliography block in the LaTeX template.
#
# --citeproc is intentionally NOT used: templates such as tcc-abnt rely on
# the native BibTeX flow (abntex2-alf style). --citeproc would intercept
# the references, resolve them internally, and inject the formatted list
# into $body$, bypassing the post-textual \bibliography{} command entirely.
# BibTeX is handled by latexmk in a subsequent step.
# ---------------------------------------------------------------------------
BIB_ARGS=""
BIB_FIELD=$(grep -m1 '^bibliography:' "$INPUT_FILE" | sed 's/^bibliography:[[:space:]]*//' | tr -d '"'"'" | tr -d '[:space:]')
if [[ -n "$BIB_FIELD" ]]; then
    BIB_FILE="${BIB_FIELD}.bib"
    if [[ -f "$BIB_FILE" ]]; then
        BIB_ARGS="--bibliography=${BIB_FILE}"
        echo "📚 Bibliography file found: ${BIB_FILE}"
    else
        echo "⚠️  Bibliography field set to '${BIB_FIELD}' but '${BIB_FILE}' was not found in the working directory."
    fi
fi

# Convert --font to boolean metadata flags for Pandoc.
FONT_ARGS=""
case "$FONT_VALUE" in
    arial)     FONT_ARGS="--metadata=font-arial:true" ;;
    helvetica) FONT_ARGS="--metadata=font-helvetica:true" ;;
    ubuntu)    FONT_ARGS="--metadata=font-ubuntu:true" ;;
    times)     FONT_ARGS="--metadata=font-times:true" ;;
esac

# Templates based on abntex2 without the 'article' option use \chapter as the
# top-level division. Pass --top-level-division=chapter so that Pandoc maps
# Markdown '#' headings to \chapter instead of \section, preventing the
# '0.1 Introduction' numbering bug caused by a missing parent chapter counter.
TOP_LEVEL_ARGS=""
case "$TEMPLATE_TYPE" in
    tcc-abnt|dissertacao-abnt|tese-abnt|relatorio-abnt)
        TOP_LEVEL_ARGS="--top-level-division=chapter"
        ;;
esac

TEMPLATE_PATH="$TEMPLATE_BASE/$TEMPLATE_TYPE/template.tex"

# Filtro de referências cruzadas (@fig:id → Figura~\ref{fig:id}).
# Activado automaticamente quando crossref.lua está presente no diretório
# de templates (montado em runtime — não requer rebuild da imagem Docker).
CROSSREF_ARGS=""
if [[ -f "${TEMPLATE_BASE}/crossref.lua" ]]; then
    CROSSREF_ARGS="--lua-filter ${TEMPLATE_BASE}/crossref.lua"
fi

pandoc "$INPUT_FILE" \
    --template="$TEMPLATE_PATH" \
    --pdf-engine=xelatex \
    $BIB_ARGS \
    $FONT_ARGS \
    $TOP_LEVEL_ARGS \
    $CROSSREF_ARGS \
    --wrap=preserve \
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
# Disable SyncTeX: not needed in this pipeline and generates a .synctex.gz
# in \$out_dir (/app) that would be left in the user's working directory.
# -interaction and other flags are injected by latexmk via %O at runtime.
\$xelatex = 'xelatex -synctex=0 %O %S';
RCEOF

# ---------------------------------------------------------------------------
# Source-change detection (logging only — latexmk handles its own deps)
#
# pandoc generates the .tex at the START of every run, so the file already
# exists when latexmk runs.  latexmk stores MD5 hashes of all input files
# in .fdb_latexmk and detects changes itself:
#
#   • Same content  → "Nothing to do" (0 xelatex passes — near-instant)
#   • Text change   → reruns xelatex once if the .aux stays stable
#   • Structural change (TOC/refs/bib) → 2–3 passes until stable
#
# Deleting .fdb_latexmk here would defeat this and force a full rebuild on
# every content edit. We keep it and let latexmk's own tracking do the work.
# The hash below is used only for the user-facing "source changed" message
# and for the .aux corruption guard that follows.
# ---------------------------------------------------------------------------
TEX_HASH_FILE="${CACHE_DIR}/.tex_hash"
NEW_HASH=$(md5sum "$OUTPUT_NAME.tex" | cut -d' ' -f1)
OLD_HASH=$(cat "$TEX_HASH_FILE" 2>/dev/null || echo "")

if [[ "$NEW_HASH" != "$OLD_HASH" ]]; then
    if [[ -n "$OLD_HASH" ]]; then
        echo "🔄 Source changed — latexmk will rerun the affected passes."
    fi
    echo "$NEW_HASH" > "$TEX_HASH_FILE"
fi

# ---------------------------------------------------------------------------
# Corrupt .aux guard
#
# When xelatex aborts mid-write (OOM, kill, -f recoverable error) the .aux
# file can be left filled with null bytes (^^@).  latexmk's own state does
# not cover this case, so the next pass reads the garbage and hits 100
# "invalid character" errors — while the old PDF (still on disk) causes the
# script to report success, silently keeping the document stale.
#
# Fix: scan the .aux for null bytes before invoking latexmk.  A healthy .aux
# is pure text and never contains them.  grep -qP '\x00' exits on the first
# match, so it costs almost nothing on valid files.  When corruption is
# detected, wipe .aux + the latexmk state so the next pass rebuilds cleanly.
# ---------------------------------------------------------------------------
AUX_FILE="${CACHE_DIR}/${DOC_STEM}.aux"
if [[ -f "$AUX_FILE" ]] && grep -qP '\x00' "$AUX_FILE" 2>/dev/null; then
    echo "⚠️  Corrupt .aux detected — clearing intermediate cache for a clean rebuild."
    rm -f "$AUX_FILE"
    rm -f "${CACHE_DIR}/${DOC_STEM}.fdb_latexmk"
    rm -f "${CACHE_DIR}/${DOC_STEM}.xdv"
fi

if [[ -f "${CACHE_DIR}/${DOC_STEM}.fdb_latexmk" ]]; then
    if [[ "$NEW_HASH" == "$OLD_HASH" ]]; then
        echo "⚡ Source unchanged — latexmk will verify dependencies (may be a no-op)."
    else
        echo "⚡ Incremental build: reusing latexmk cache from previous run."
    fi
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
# When a .bib file is present, Pandoc populates $bibliography$ in the
# template, causing \bibliography{} to be emitted in the .tex. latexmk
# must then run BibTeX to generate the .bbl file. The -bibtex- flag is
# therefore replaced with -bibtex so latexmk schedules BibTeX automatically
# whenever \bibliography{} is detected in the .tex source.
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
        -bibtex \
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

# PDF existence is the authoritative success criterion: xelatex running in
# force mode (-f) may exit non-zero even after producing a valid PDF (e.g.
# when a recoverable error such as a missing-image placeholder was hit).
# Only propagate the latexmk exit code when no PDF was generated at all.
if [[ -f "${OUTPUT_NAME}.pdf" ]]; then
    echo "✅ PDF generated successfully: ${OUTPUT_NAME}.pdf"
    echo "PROGRESS:100%"
    sync
elif [[ "$LATEXMK_EXIT" -ne 0 ]]; then
    # latexmk failed and produced no PDF — let the cleanup trap handle cache wiping.
    exit "$LATEXMK_EXIT"
else
    echo "❌ Error: PDF was not generated."
    exit 1
fi

echo "🎉 Process complete!"

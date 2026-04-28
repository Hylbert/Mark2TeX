#!/bin/bash
set -e

# Inputs from arguments
INPUT_FILE=$1
TEMPLATE_TYPE=$2
OUTPUT_NAME="output"

echo "🚀 Starting build for $INPUT_FILE using template $TEMPLATE_TYPE..."

# 1. Pandoc Conversion to LaTeX
# We use --template to inject the metadata and body into our parameterized .tex file
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

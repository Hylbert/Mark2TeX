# LateXOS Build Orchestrator

# Default values
TEMPLATE ?= tcc
INPUT ?= Reconhecimento_de_gestos.md

.PHONY: build-image compile clean

# Build the Docker image
build-image:
	docker build -t latexos .

# Compile the document using the Docker container
# We map the current directory to /app inside the container
# --user $(id -u):$(id -g) ensures files created by Docker belong to the host user
compile:
	docker run --rm \
		--user $(shell id -u):$(shell id -g) \
		-v $(PWD):/app \
		latexos \
		bash /app/scripts/build.sh $(INPUT) $(TEMPLATE)

clean:
	rm -f *.aux *.log *.out *.toc *.lot *.lof *.bbl *.blg *.synctex.gz *.tex output.pdf

FROM ubuntu:22.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Accept Microsoft EULA for mscorefonts
RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections

# Install essential tools and LaTeX distribution
RUN apt-get update && apt-get install -y \
    curl \
    texlive-xetex \
    texlive-latex-extra \
    texlive-publishers \
    texlive-lang-portuguese \
    texlive-fonts-recommended \
    texlive-bibtex-extra \
    latexmk \
    ttf-mscorefonts-installer \
    make \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install latest Pandoc from official releases
RUN curl -LO https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-1-amd64.deb && \
    dpkg -i pandoc-3.1.11-1-amd64.deb && \
    rm pandoc-3.1.11-1-amd64.deb

# Create a non-root user for security and file permission management
RUN useradd -m mark2tex
USER mark2tex
WORKDIR /app

# Copy scripts and templates into the image
COPY --chown=mark2tex:mark2tex bin/ /opt/mark2tex/bin/
COPY --chown=mark2tex:mark2tex templates/ /opt/mark2tex/templates/
RUN chmod +x /opt/mark2tex/bin/*.sh

# Default command
CMD ["/bin/bash"]

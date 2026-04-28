# Mark2TeX

Ferramenta de automação para documentos acadêmicos que desacopla o conteúdo (Markdown) da formatação (LaTeX/ABNT).

## 🚀 Início Rápido

### Pré-requisitos
- Docker instalado

### Instalação e Uso
1. Clone o repositório: `git clone https://github.com/Hylbert/Mark2TeX.git`
2. Construa a imagem: `make build-image`
3. Compile seu documento: `make compile TEMPLATE=tcc INPUT=meu_arquivo.md`

## 📂 Estrutura do Projeto
- `bin/`: Scripts de execução do pipeline.
- `templates/`: Modelos LaTeX parametrizados (TCC, Artigo, Projeto).
- `examples/`: Boilerplates de Markdown para cada tipo de documento.
- `docs/`: Manual detalhado de uso e customização.

## 🛠️ Como funciona
O Mark2TeX utiliza um pipeline dockerizado:
Markdown (.md) $\rightarrow$ Pandoc $\rightarrow$ XeLaTeX $\rightarrow$ PDF

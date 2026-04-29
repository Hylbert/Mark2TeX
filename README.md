<p align="center">
  <img src="assets/logo.png" alt="Mark2TeX" width="150" height="150">
</p>

<h1 align="center">Mark2TeX</h1>

<div align="center">
  <strong>🚀 A automação definitiva para documentos acadêmicos ABNT 🎓</strong><br>
  Um sistema elegante e open-source que desacopla o conteúdo (Markdown) da formatação (LaTeX), focando em velocidade e rigor acadêmico.<br>
  <sub>Disponível via Docker para Linux, macOS e Windows.</sub>
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/workflow-GitFlow-orange.svg" alt="GitFlow">
  <img src="https://img.shields.io/badge/version-SemVer-green.svg" alt="SemVer">
</div>

<div align="center">
  <h3>
    <a href="#✨-principais-funcionalidades">
      Funcionalidades
    </a>
    <span> | </span>
    <a href="#🚀-começando-rapidamente">
      Instalação
    </a>
    <span> | </span>
    <a href="#📂-organização-do-projeto">
      Estrutura
    </a>
    <span> | </span>
    <a href=".github/CONTRIBUTING.md">
      Contribuição
    </a>
  </h3>
</div>

<div align="center">
  <sub>Construído com ❤︎ por <a href="https://github.com/Hylbert">Hylbert</a> e contribuidores.</sub>
</div>

<br />

## ✨ Principais Funcionalidades

- 🚀 **Pipeline Dockerizado**: Zero instalação de distribuições TeX locais. Tudo roda em um container isolado e configurado.
- 📄 **Templates Parametrizados**: Suporte nativo para os formatos mais exigidos:
  - **TCC**: Layout completo de monografia (Capa, Folha de Rosto, Resumos, Sumário, etc.).
  - **Artigo**: Formatação compacta e profissional para publicações científicas.
  - **Projeto**: Estrutura ideal para propostas de pesquisa e cronogramas.
- 🛠️ **Automação Total**: Integração poderosa entre `Pandoc` e `XeLaTeX` para gerar PDFs de alta fidelidade.
- 🔄 **Live Preview (Watch Mode)**: Compilação automática em tempo real. Salve seu Markdown e veja o PDF atualizar instantaneamente.
- 📚 **Gestão de Bibliografia**: Suporte automatizado ao BibTeX para referências bibliográficas rigorosas.
- 🖋️ **Tipografia Profissional**: Configuração nativa de fontes Microsoft (Times New Roman) para conformidade total com a ABNT.

## ❓ Por que o Mark2TeX?

1. **Foco no Conteúdo**: O autor não deve perder horas lutando com erros de compilação do LaTeX ou ajustando margens. O Mark2TeX permite que você foque na escrita, enquanto a ferramenta cuida da norma.
2. **Portabilidade**: Graças ao Docker, o projeto é idêntico em qualquer máquina. Se funciona no seu computador, funcionará no do seu orientador.
3. **Acessibilidade**: Torna a produção de documentos de alta qualidade acessível a quem prefere a simplicidade do Markdown, mas precisa do rigor do LaTeX.

## 🚀 Começando Rapidamente

![platform](https://img.shields.io/static/v1.svg?label=Platform&message=Docker%20(Linux%20|%20macOS%20|%20Windows)&style=for-the-badge)

### 🛠️ Configuração do Ambiente
Se você ainda não tem o Docker ou Python instalados, utilize nossos scripts de configuração rápida:
- **Linux:** `bash scripts/setup/setup_linux.sh`
- **macOS:** `bash scripts/setup/setup_macos.sh`
- **Windows:** `powershell .\scripts\setup\setup_windows.ps1`

*Esses scripts detectam automaticamente o que está faltando e instalam as dependências necessárias.*

### 🛠️ Instalação e Uso

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Hylbert/Mark2TeX.git
   cd Mark2TeX
   ```

2. **Construa a imagem do ambiente**
   ```bash
   make build-image
   ```

3. **Gere seu PDF**
   Use o comando `make compile` passando o template desejado e o seu arquivo Markdown:
   ```bash
   make compile TEMPLATE=tcc INPUT=meu_trabalho.md
   ```
   *O arquivo final `output.pdf` será gerado na raiz do projeto.*

## 📂 Organização do Projeto

- `bin/` $\rightarrow$ Scripts core de compilação e automação (`build.sh`, `watch.sh`).
- `templates/` $\rightarrow$ Modelos `.tex` parametrizados.
- `examples/` $\rightarrow$ Boilerplates de Markdown para início rápido.
- `docs/` $\rightarrow$ Manual técnico e guias de customização.

## 🤝 Contribuição

O Mark2TeX é um projeto open-source e cresce com a ajuda da comunidade. Se você deseja adicionar novos templates ou melhorar o pipeline, por favor, leia nosso [Guia de Contribuição](.github/CONTRIBUTING.md) e nosso [Código de Conduta](.github/CODE_OF_CONDUCT.md).

---
<div align="center">
  Desenvolvido para simplificar a vida de estudantes e pesquisadores. 🎓
</div>

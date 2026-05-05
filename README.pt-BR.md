<p align="center">
  <img src="assets/logo.png" alt="Mark2TeX" width="150" height="150">
</p>

<h1 align="center">Mark2TeX</h1>

<div align="center">
  <strong><a href="README.md">English</a> | <span>Português (Brasil)</span></strong>
</div>

<div align="center">
  <strong>Escreva Markdown. Receba um PDF acadêmico impecável.</strong><br>
  Pipeline Dockerizado com TUI interativa para documentos com qualidade LaTeX — sem instalar TeX.
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/workflow-GitFlow-orange.svg" alt="GitFlow">
  <img src="https://img.shields.io/badge/version-SemVer-green.svg" alt="SemVer">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="Licença MIT">
</div>

<br>

## O que é o Mark2TeX?

Mark2TeX é uma ferramenta de linha de comando que converte arquivos Markdown em PDFs prontos para publicação, usando Pandoc, XeLaTeX e templates LaTeX pré-construídos — tudo dentro de um container Docker. Você escreve texto simples; o Mark2TeX cuida da tipografia.

**Por que usar Mark2TeX em vez de escrever LaTeX diretamente?**

| | LaTeX | Mark2TeX |
|---|---|---|
| Curva de aprendizado | Íngreme | Markdown simples |
| Configuração do ambiente | Distribuição TeX 4 GB+ | Apenas Docker |
| Mensagens de erro | Logs crípticos | Tradução legível |
| Feedback ao vivo | Recompilação manual | Watch mode automático |

## Quickstart

```bash
# 1 — instalar (requer Python 3.10+ e Docker)
pipx install mark2tex

# 2 — executar (a imagem Docker é baixada automaticamente no primeiro uso)
mark2tex
```

> **Nota:** Na primeira execução, o Mark2TeX baixa automaticamente a imagem `mark2tex` do Docker Hub. Isso requer conexão com a internet e pode levar alguns minutos dependendo da sua velocidade. Execuções posteriores reutilizam a imagem em cache.
>
> **Sem internet?** Se o Docker Hub estiver inacessível, o Mark2TeX fará o build da imagem localmente a partir do `Dockerfile` incluído no pacote. Você também pode executar `make build-image` manualmente a qualquer momento.

## A TUI em destaque

<p align="center">
  <img src="assets/dashboard_v2_m2t.png" alt="Dashboard Mark2TeX" width="800">
</p>

1. Selecione um arquivo `.md` no painel esquerdo.
2. Escolha um template (`tcc`, `artigo-ieee`, `doc-tecnica`, `projeto`, `apresentacao`).
3. Opcionalmente escolha uma fonte (`--font arial | helvetica | times | ubuntu`).
4. Pressione **`c`** para compilar ou **`w`** para ativar o Watch Mode.

### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `c` | Compilar |
| `w` | Ativar/desativar Watch Mode |
| `F1` / `?` | Ajuda |
| `Esc` / `q` | Menu global |

## Funcionalidades

- **Builds Dockerizados** — sem instalação local de LaTeX; resultado idêntico em qualquer máquina.
- **TUI interativa** — navegador de arquivos, seletor de template, console de log em tempo real e barra de progresso criados com [Textual](https://github.com/Textualize/textual).
- **Watch mode** — recompilação automática a cada salvamento do arquivo.
- **Logs legíveis por humanos** — a saída bruta do XeLaTeX é analisada e traduzida para mensagens em linguagem simples.
- **Seleção de fonte** — escolha entre Liberation Sans (compatível com Arial), Nimbus Sans (Helvetica), Liberation Serif (compatível com Times) e Ubuntu por documento.
- **Suporte a bibliografia** — BibTeX via Pandoc + XeLaTeX; basta adicionar um `referencias.bib` ao lado do seu `.md`.
- **Fluxo orientado à ABNT** — templates construídos segundo as normas acadêmicas brasileiras.

## Templates Disponíveis

| Template | Finalidade |
|---|---|
| `tcc` | Trabalho de Conclusão de Curso (ABNT) |
| `artigo-ieee` | Artigo para conferência IEEE |
| `doc-tecnica` | Documentação técnica |
| `projeto` | Proposta de projeto |
| `apresentacao` | Apresentação baseada em Beamer |

## Roadmap

- [ ] Templates ABNT adicionais (artigo, dissertação)
- [ ] Prévia visual de fonte e template
- [ ] Comando `mark2tex new <template>` para criar scaffolds
- [ ] Instalador nativo para Windows
- [ ] Integração com GitHub Actions para geração de PDF em CI

Acompanhe as [issues abertas](https://github.com/Hylbert/Mark2TeX/issues) ou sugira novas funcionalidades.

## Como contribuir

O Mark2TeX cresce com a ajuda da comunidade. Todos os níveis de habilidade são bem-vindos — desde correção de typos até a criação de novos templates.

1. Leia o [Guia de Contribuição](.github/CONTRIBUTING.md).
2. Leia o [Código de Conduta](.github/CODE_OF_CONDUCT.md).
3. Abra uma issue antes de mudanças grandes para alinhar a direção.
4. Faça fork, crie uma branch, implemente e abra um pull request.

Somos gratos por cada contribuição. ✨

## Licença

Mark2TeX é distribuído sob a [Licença MIT](LICENSE).

---
<div align="center">
  Desenvolvido com ❤︎ por <a href="https://github.com/Hylbert">Hylbert</a> e <a href="https://github.com/Hylbert/Mark2TeX/graphs/contributors">contribuidores</a>.
</div>

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

> **Por que `pipx`?**
> O Mark2TeX é uma ferramenta CLI, não uma biblioteca. O `pipx` instala ferramentas
> CLI Python em ambientes isolados automaticamente — sem sujar o Python do sistema
> nem exigir `venv` manual. Se você ainda não tem o `pipx`:
>
> ```bash
> # Ubuntu / Debian
> sudo apt install pipx && pipx ensurepath
>
> # macOS
> brew install pipx && pipx ensurepath
>
> # Windows (PowerShell)
> python -m pip install --user pipx
> python -m pipx ensurepath
> ```
>
> Reinicie o terminal após executar `ensurepath`.

```bash
# 1 — instalar (requer Python 3.10+ e Docker)
pipx install mark2tex

# 2 — verificar o ambiente (recomendado na primeira instalação)
mark2tex check

# 3 — abrir a TUI (a imagem Docker é baixada automaticamente)
mark2tex
```

> **Primeira execução:** O Mark2TeX baixa automaticamente a imagem `mark2tex` do Docker Hub com
> uma **barra de progresso Rich visual** — uma barra por layer mostrando velocidade de download,
> tamanho e tempo estimado. Requer conexão com a internet; pode levar alguns minutos dependendo
> da sua velocidade. Execuções posteriores reutilizam a imagem em cache.
>
> **Sem internet?** Se o Docker Hub estiver inacessível, o Mark2TeX faz o build da imagem
> localmente a partir do `Dockerfile` incluído no pacote (spinner exibido durante os steps).
> Você também pode executar `make build-image` manualmente a qualquer momento.

> **Tela de boas-vindas:** Na primeira abertura, uma tela de boas-vindas guia você pelo fluxo
> de uso. Clique em **"Inicializar projeto aqui"** para copiar um arquivo `.md` de exemplo
> pronto para editar diretamente no seu diretório atual — sem precisar sair do app. Você também
> pode rodar `mark2tex init` no terminal a qualquer momento para fazer o mesmo.

## Comandos CLI

| Comando | Descrição |
|---|---|
| `mark2tex` | Abre a TUI interativa (padrão) |
| `mark2tex check` | Executa diagnóstico completo do sistema |
| `mark2tex init [--template NOME]` | Copia um template + exemplo para o diretório atual |
| `mark2tex restore <arquivo>` | Restaura um `.md` ao estado anterior à injeção de YAML |
| `mark2tex clean [arquivo]` | Remove o cache latexmk — todos os docs ou apenas um específico |
| `mark2tex uninstall` | Remove imagens Docker, dados do usuário e configs — execute antes de `pipx uninstall mark2tex` |
| `mark2tex doctor` | Alias para `check` *(depreciado — use `check`)* |

### `mark2tex check` — Relatório de Saúde do Sistema

Executa seis verificações e exibe um relatório visual:

```
──────────── Mark2TeX — Diagnóstico do Sistema  v0.2.2 ────────────

✅   Mark2TeX          0.2.2
✅   Docker (binário)  /usr/bin/docker
✅   Docker (daemon)   active
✅   Imagem mark2tex   mark2tex:latest (1 143 MB)
⚠️   Pandoc            not found (optional)
                          Pandoc está na imagem Docker — instalação no host não é necessária.
✅   Python            3.12.3
✅   Espaço em disco   145.0 GB free (320.1 GB used / 465.1 GB total)  ·  imagem: 1 143 MB

───────────────────────────────────────────────────────────────────
  5 OK  ·  1 aviso  ·  0 erros

  Verifique os avisos acima antes de compilar.
```

Código de saída `0` quando não há erros; código `1` quando pelo menos uma verificação crítica falha — compatível com scripts e pipelines CI.

## A TUI em destaque

<p align="center">
  <img src="assets/dashboard_v2_m2t.png" alt="Dashboard Mark2TeX" width="800">
</p>

1. Selecione um arquivo `.md` no painel esquerdo.
2. Escolha um template (`tcc-abnt`, `artigo-ieee`, `doc-tecnica`, `projeto`).
3. Opcionalmente escolha uma fonte (`Liberation Serif`, `Liberation Sans`, `Nimbus Sans`, `Ubuntu`).
4. Pressione **`c`** para compilar ou **`w`** para ativar o Watch Mode.

### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `c` | Compilar |
| `w` | Ativar/desativar Watch Mode |
| `Enter` | Entrar na pasta / selecionar arquivo |
| `F1` / `?` | Ajuda |
| `Esc` / `q` | Menu global |

## Funcionalidades

- **Builds Dockerizados** — sem instalação local de LaTeX; resultado idêntico em qualquer máquina.
- **TUI interativa** — navegador de arquivos, seletor de template, console de log em tempo real e barra de progresso criados com [Textual](https://github.com/Textualize/textual).
- **Navegação de diretórios** — o painel de arquivos abre no diretório de trabalho atual. Subpastas são listadas antes dos arquivos `.md`; pressione `Enter` em uma pasta para entrar nela. Um item `../` no topo da lista volta para a pasta pai.
- **Onboarding no primeiro uso** — tela de boas-vindas exibida na primeira abertura com botão **"Inicializar projeto aqui"** que copia um `.md` de exemplo no diretório atual sem sair do app.
- **Watch mode** — recompilação automática a cada salvamento do arquivo; arquivos temporários/swap (`.swp`, `.bak`, `~`) são ignorados; debounce de 1,5 s evita duplos disparos em editores com escrita em duas etapas (ex.: Obsidian).
- **Builds incrementais** — o latexmk persiste arquivos intermediários (`.aux`, `.fdb_latexmk`, `.fls`) em um diretório de cache padrão do SO. Recompilação após uma alteração de uma linha leva ~6 s em vez de ~18 s em um documento de 15 páginas.
- **Timeout de compilação** — timeout padrão de 5 minutos (configurável via `MARK2TEX_TIMEOUT`) impede que builds travados bloqueiem a interface indefinidamente.
- **Worker exclusivo** — pressionar `c` duas vezes ou um disparo do Watch Mode durante um build cancela o worker anterior antes de iniciar um novo, eliminando linhas de log entrecruzadas.
- **Validador de frontmatter** — antes de cada compilação, o YAML frontmatter é verificado: campos obrigatórios ausentes, valores placeholder não preenchidos, template incompatível e códigos `lang` inválidos. Avisos aparecem no console da TUI; erros críticos abortam o build antecipadamente.
- **Troca de template** — mudar de template na TUI atualiza cirurgicamente `template:` e `date:` no frontmatter, adiciona campos ausentes com placeholders e remove campos exclusivos do template antigo — sem tocar nos valores já preenchidos.
- **Logs legíveis por humanos** — a saída bruta do XeLaTeX é analisada e traduzida para mensagens em linguagem simples.
- **Seleção de fonte** — escolha entre Liberation Sans (Arial), Nimbus Sans (Helvetica), Liberation Serif (Times) e Ubuntu por documento.
- **Suporte a bibliografia** — BibTeX via Pandoc + XeLaTeX; basta adicionar um `referencias.bib` ao lado do `.md`. O BibTeX só é invocado quando o documento contém marcadores de citação reais.
- **Diagnóstico do sistema** — `mark2tex check` verifica o ambiente antes de compilar.
- **Progresso Rich no pull da imagem** — barras de progresso por layer com velocidade e ETA na primeira execução.
- **Injeção de YAML frontmatter** — arquivos sem cabeçalho YAML são destacados em âmbar na TUI; um modal de confirmação injeta o frontmatter automaticamente antes de compilar. Um backup é salvo em `~/.local/share/mark2tex/backups/` e pode ser restaurado a qualquer momento com `mark2tex restore <arquivo>`.
- **Gerência de cache de build** — `mark2tex clean [arquivo]` remove o cache latexmk de todos os documentos ou de um específico.
- **Fluxo orientado à ABNT** — templates construídos segundo as normas acadêmicas brasileiras, com `polyglossia` para hifenização correta em pt-BR e `setspace` para o espaçamento 1,5 exigido pela ABNT.

## Templates Disponíveis

| Template | Finalidade |
|---|---|
| `tcc-abnt` | Trabalho de Conclusão de Curso (ABNT) |
| `artigo-ieee` | Artigo para conferência IEEE |
| `artigo-abnt` | Artigo ABNT |
| `doc-tecnica` | Documentação técnica |
| `projeto` | Proposta de projeto |

## Roadmap

- [x] Diagnóstico do sistema (`mark2tex check`)
- [x] Onboarding no primeiro uso com Rich Progress para pull da imagem Docker
- [x] Tela de boas-vindas com fluxo guiado e botão "Inicializar projeto aqui"
- [x] `mark2tex init` — criar scaffold de template no diretório atual
- [x] Injeção automática de YAML frontmatter em arquivos sem cabeçalho (com backup e restore)
- [x] Navegação de diretórios no painel de arquivos (subpastas + navegação `../`)
- [x] Validador de frontmatter — campos obrigatórios, placeholders, incompatibilidade de template, validação de lang
- [x] Troca de template — preservar valores do usuário ao trocar de template na TUI
- [x] Builds incrementais com latexmk e cache no diretório de usuário do SO
- [x] Timeout de compilação com override via `MARK2TEX_TIMEOUT`
- [x] Worker exclusivo de compilação (cancela e reinicia)
- [x] `mark2tex clean` — limpar cache latexmk de build
- [x] Correção de race condition no Watch Mode (abortar container antigo antes do novo Pandoc)
- [ ] Templates ABNT adicionais (dissertação, apresentação)
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

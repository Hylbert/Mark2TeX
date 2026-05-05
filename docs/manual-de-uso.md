# Manual de Uso — Mark2TeX

> **Sobre este documento**
> O README cobre instalação, quickstart e visão geral.
> Este manual cobre uso avançado: configuração detalhada de cada template,
> Watch Mode, resolução de erros do XeLaTeX e integração em pipelines de CI.

## Índice

1. [Como o Mark2TeX funciona por dentro](#1-como-o-mark2tex-funciona-por-dentro)
2. [O arquivo Markdown — referência completa do YAML](#2-o-arquivo-markdown--referência-completa-do-yaml)
3. [Templates — guia por template](#3-templates--guia-por-template)
4. [Fontes — quando usar cada uma](#4-fontes--quando-usar-cada-uma)
5. [BibTeX — bibliografia passo a passo](#5-bibtex--bibliografia-passo-a-passo)
6. [Watch Mode — como funciona](#6-watch-mode--como-funciona)
7. [Docker internals — o que está na imagem](#7-docker-internals--o-que-está-na-imagem)
8. [Diagnóstico do sistema (`mark2tex check`)](#8-diagnóstico-do-sistema-mark2tex-check)
9. [Erros comuns do XeLaTeX — o que significam](#9-erros-comuns-do-xelatex--o-que-significam)
10. [Integração com CI/CD](#10-integração-com-cicd)

---

## 1. Como o Mark2TeX funciona por dentro

Entender o pipeline evita surpresas quando algo dá errado.

```
┌─────────────────────────────────────────────────────────────────┐
│  Host (sua máquina)                                             │
│                                                                 │
│  arquivo.md ──► mark2tex CLI ──► docker run mark2tex:latest     │
│                     │                        │                  │
│                     │            ┌───────────▼──────────────┐   │
│                     │            │  Container               │   │
│                     │            │  pandoc → arquivo.tex    │   │
│                     │            │  xelatex (2×) → .pdf     │   │
│                     │            │  biber (se .bib) → .bbl  │   │
│                     └────────────►  saída copiada de volta   │   │
│                                  └──────────────────────────┘   │
│  arquivo.pdf ◄── mesmo diretório do .md                         │
└─────────────────────────────────────────────────────────────────┘
```

**Por que o XeLaTeX roda duas vezes?**
A primeira passagem gera referências internas (numeração de seções, figuras,
tabelas). A segunda resolve essas referências no documento final. Com
bibliografia, uma passagem do Biber é intercalada entre as duas.

**Onde o PDF é gerado?**
Sempre no mesmo diretório do arquivo `.md` de origem. Arquivos intermediários
(`.aux`, `.log`, `.toc`) são descartados dentro do container; somente o `.pdf`
final é copiado de volta para o host.

---

## 2. O arquivo Markdown — referência completa do YAML

O cabeçalho YAML controla metadados, capa, sumário, norma e compilação.
Ele deve estar entre `---` no início do arquivo, antes de qualquer conteúdo.

### 2.1 Campos universais (todos os templates)

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `title` | string | — | Título principal; aparece na capa e nos metadados do PDF |
| `author` | string | — | Nome completo do autor |
| `date` | string | data atual | Data de entrega (`YYYY-MM-DD` ou texto livre) |
| `lang` | string | `pt-BR` | Idioma; afeta hifenização e rótulos automáticos |
| `bibliography` | string | — | Caminho relativo para o `.bib` (ex: `referencias.bib`) |
| `font` | string | `liberation-serif` | Fonte tipográfica (ver [seção 4](#4-fontes--quando-usar-cada-uma)) |

> **Dica:** Envolva valores com caracteres especiais LaTeX em aspas simples:
> ```yaml
> title: 'Análise de $\alpha$-cetoacidos em amostras clínicas'
> ```

### 2.2 Campos específicos — `tcc-abnt`

| Campo | Obrigatório | Descrição |
|---|---|---|
| `institution` | Sim | Nome da instituição (capa) |
| `campus` | Não | Campus ou unidade |
| `department` | Não | Departamento ou curso |
| `course` | Não | Nome do curso |
| `advisor` | Sim | Nome do orientador |
| `coadvisor` | Não | Nome do coorientador |
| `city` | Sim | Cidade (capa e folha de rosto) |
| `year` | Sim | Ano de defesa (entre aspas: `"2026"`) |
| `abstract-pt` | Sim | Resumo em português (texto corrido, sem quebras de linha) |
| `abstract-en` | Sim | Abstract em inglês |
| `acknowledgments` | Não | Agradecimentos (texto corrido) |
| `siglas` | Não | Lista de abreviaturas em LaTeX (ver exemplo abaixo) |
| `simbolos` | Não | Lista de símbolos matemáticos em LaTeX |

**Exemplo completo `tcc-abnt`:**

```yaml
---
title: "Detecção de Anomalias em Sensores Industriais com Isolation Forest"
author: "Hylbert Rodrigues"
date: "2026-05-05"
institution: Instituto de Desenvolvimento Tecnológico
campus: Manaus
department: Engenharia de Software
course: Sistemas de Informação
advisor: Prof. Dr. Fulano de Tal
coadvisor: Prof. Me. Ciclano da Silva
city: Manaus
year: "2026"
lang: pt-BR
abstract-pt: 'Este trabalho propõe um sistema de detecção de anomalias...'
abstract-en: 'This work proposes an anomaly detection system...'
acknowledgments: 'Agradeço ao INDT pelo suporte durante a pesquisa.'
siglas: \begin{description}
  \item[INDT] Instituto de Desenvolvimento Tecnológico
  \item[PDF]  Portable Document Format
  \end{description}
bibliography: referencias.bib
font: liberation-serif
---
```

### 2.3 Campos específicos — `artigo-ieee`

| Campo | Obrigatório | Descrição |
|---|---|---|
| `abstract` | Sim | Abstract do artigo (campo único, padrão IEEE) |
| `keywords` | Não | Palavras-chave separadas por vírgula |

### 2.4 Campos específicos — `artigo-abnt`

Mesmos campos do `tcc-abnt`, com `abstract-pt` e `abstract-en`, mais:

| Campo | Obrigatório | Descrição |
|---|---|---|
| `journal` | Não | Nome do periódico de destino |
| `keywords-pt` | Não | Palavras-chave em português |
| `keywords-en` | Não | Keywords em inglês |

### 2.5 Campos específicos — `doc-tecnica` e `projeto`

| Campo | Obrigatório | Descrição |
|---|---|---|
| `version` | Não | Versão do documento (ex: `"1.0.0"`) |
| `status` | Não | Status (`Rascunho`, `Aprovado`, `Em revisão`) |
| `team` | Não | Equipe ou setor responsável |

---

## 3. Templates — guia por template

### `tcc-abnt`

Produz um TCC completo segundo a ABNT NBR 14724. Inclui automaticamente:
capa, folha de rosto, folha de aprovação (em branco), resumo, abstract,
lista de siglas/símbolos, sumário, corpo do texto e referências bibliográficas.

**Estrutura de diretório recomendada:**

```
projeto/
├── meu-tcc.md
├── referencias.bib
└── figuras/
    └── diagrama.png
```

**Inserindo figuras:**

```markdown
![Legenda da figura](figuras/diagrama.png){width=80%}
```

O caminho é relativo ao `.md`. A largura aceita `%` (relativo à coluna de texto)
ou `cm`.

---

### `artigo-ieee`

Produz layout de duas colunas padrão IEEE. Não inclui sumário.
Referências seguem o estilo numérico IEEE.

**Citação no texto:**

```markdown
Conforme demonstrado em \cite{liu2020isolation}, o algoritmo...
```

**Figuras em largura total (duas colunas):**

Figuras largas precisam do ambiente `figure*` do LaTeX.
Use um bloco raw para isso:

```markdown
```{=latex}
\begin{figure*}[ht]
  \centering
  \includegraphics[width=\textwidth]{figuras/resultado.png}
  \caption{Resultado geral do experimento.}
\end{figure*}
```
```

---

### `artigo-abnt`

Layout de coluna única. Citações seguem ABNT NBR 6023 (autor-data).

**Citação no texto:**

```markdown
# Citação simples
A detecção de anomalias \cite{liu2020isolation} tem sido amplamente...

# Com número de página
Conforme (LIU, 2020, p. 42), o método...
```

---

### `doc-tecnica`

Indicado para READMEs internos, especificações e guias de implantação.
Não exige campos de capa completos — basta `title`, `author` e `date`.
Inclui cabeçalho com número de versão e status do documento.

---

### `projeto`

Indicado para propostas de projeto, planos de trabalho e cronogramas.
Suporta tabelas de cronograma em Markdown nativamente.

---

## 4. Fontes — quando usar cada uma

O Mark2TeX usa fontes metricamente compatíveis com as exigidas por normas
acadêmicas, distribuídas livremente sob licença open-source.

| Valor `font` | Família real | Compatível com | Indicada para |
|---|---|---|---|
| `liberation-serif` | Liberation Serif | Times New Roman | TCC, artigos ABNT (padrão) |
| `liberation-sans` | Liberation Sans | Arial | Apresentações, doc-tecnica |
| `nimbus-sans` | Nimbus Sans | Helvetica | Artigos IEEE, publicações internacionais |
| `ubuntu` | Ubuntu | — | Documentação técnica, projetos digitais |

**Como especificar no YAML:**

```yaml
font: nimbus-sans
```

**Como sobrescrever via CLI (ignora o valor no YAML):**

```bash
mark2tex compile meu-artigo.md --template artigo-ieee --font nimbus-sans
```

> **Nota ABNT:** A NBR 14724 exige "Arial ou Times New Roman, tamanho 12".
> Use `liberation-sans` (Arial) ou `liberation-serif` (Times) para conformidade.

---

## 5. BibTeX — bibliografia passo a passo

### 5.1 Criando o arquivo `.bib`

Crie `referencias.bib` no mesmo diretório do seu `.md`:

```bibtex
@article{liu2020isolation,
  author  = {Liu, Fei Tony and Ting, Kai Ming and Zhou, Zhi-Hua},
  title   = {Isolation-Based Anomaly Detection},
  journal = {ACM Transactions on Knowledge Discovery from Data},
  year    = {2012},
  volume  = {6},
  number  = {1},
  pages   = {1--39},
  doi     = {10.1145/2133360.2133363},
}

@book{abnt2011nbr,
  author    = {{Associação Brasileira de Normas Técnicas}},
  title     = {{NBR 14724}: Informação e documentação},
  year      = {2011},
  address   = {Rio de Janeiro},
  publisher = {ABNT},
}
```

**Tipos de entrada mais usados:** `@article`, `@book`, `@inproceedings`,
`@techreport`, `@misc` (para sites, com campos `url` e `urldate`).

### 5.2 Declarando no YAML

```yaml
bibliography: referencias.bib
```

O caminho é relativo ao arquivo `.md`. Se o `.bib` estiver em outro diretório:

```yaml
bibliography: ../shared/referencias.bib
```

### 5.3 Citando no texto

```markdown
# Citação simples
O algoritmo proposto por \cite{liu2020isolation} apresenta...

# Com número de página (ABNT)
Segundo \citeonline{liu2020isolation} (p. 15), a isolação...

# Múltiplas referências
Vários estudos \cite{liu2020isolation,abnt2011nbr} demonstram...
```

### 5.4 Onde a lista de referências aparece

O Mark2TeX insere as referências automaticamente ao final do documento,
após o último capítulo. Não é necessário adicionar nenhuma seção manual.

### 5.5 Fontes de entrada `.bib` confiáveis

- **Google Scholar** → ❝ → BibTeX
- **IEEE Xplore** → botão "Cite This" → BibTeX
- **ACM Digital Library** → Export Citation → BibTeX

---

## 6. Watch Mode — como funciona

Ao pressionar `w` na TUI (ou passar `--watch` na CLI), o Mark2TeX inicia
um observador de arquivo baseado na biblioteca
[watchdog](https://github.com/gorakhargosh/watchdog).

**O que é monitorado:**

- O arquivo `.md` selecionado
- O arquivo `.bib` referenciado no YAML (se existir)
- Arquivos de imagem no mesmo diretório referenciados no `.md`

**Debounce de 800 ms:** múltiplos salvamentos rápidos geram apenas
uma compilação. O valor é ajustável via variável de ambiente:

```bash
MARK2TEX_WATCH_DEBOUNCE=2000 mark2tex  # debounce de 2 s
```

**Editores com salvamento automático (VS Code `formatOnSave`, JetBrains
`autosave`):** se o intervalo entre salvamentos for maior que 800 ms,
cada salvamento dispara uma compilação. Desative o autosave agressivo
ou aumente o debounce conforme acima.

**Como parar o Watch Mode:**

- Pressione `w` novamente na TUI
- Ou `Ctrl+C` se estiver rodando via CLI

---

## 7. Docker internals — o que está na imagem

A imagem `mark2tex:latest` (~1,1 GB) contém:

| Componente | Versão | Função |
|---|---|---|
| Ubuntu 22.04 LTS | — | Base do container |
| TeX Live (selecionado) | 2023 | Motor XeLaTeX + pacotes ABNT/IEEE |
| Pandoc | 3.x | Conversão Markdown → LaTeX |
| Biber | 2.x | Processamento de bibliography BibTeX |
| Fontes Liberation | — | Equivalentes Arial/Times open-source |
| Fontes Nimbus Sans | — | Equivalente Helvetica open-source |
| Fonte Ubuntu | — | Fonte Ubuntu oficial |

### 7.1 Build manual da imagem

Necessário apenas se você modificou o `Dockerfile` ou está offline:

```bash
# Na raiz do repositório clonado
make build-image

# Ou diretamente
docker build -t mark2tex:latest .
```

### 7.2 Inspecionar o que está instalado

```bash
# Abrir shell interativo dentro do container
docker run --rm -it mark2tex:latest bash

# Dentro do container:
pandoc --version
xelatex --version
biber --version
fc-list | grep -i liberation   # listar fontes Liberation disponíveis
```

### 7.3 Limpar a imagem

```bash
# Via CLI Mark2TeX
mark2tex uninstall

# Ou diretamente
docker rmi mark2tex:latest
```

---

## 8. Diagnóstico do sistema (`mark2tex check`)

### 8.1 O que cada probe verifica

| Probe | Severidade se falhar | O que analisa |
|---|---|---|
| **Mark2TeX** | Aviso | Versão instalada via `importlib.metadata` |
| **Docker (binário)** | ❌ Erro crítico | `docker` no PATH via `shutil.which` |
| **Docker (daemon)** | ❌ Erro crítico | `docker info` com timeout de 8 s |
| **Imagem mark2tex** | ⚠️ Aviso | `docker images mark2tex:latest` via SDK Python |
| **Pandoc** | ⚠️ Aviso | `pandoc` no PATH — opcional, já está na imagem |
| **Python** | ❌ Erro crítico | `sys.version_info >= (3, 10)` |
| **Espaço em disco** | ⚠️ Aviso | `shutil.disk_usage(Path.home())` — limiar 2 GB |

### 8.2 Tabela de troubleshooting

| Probe falhou | Causa mais comum | Solução |
|---|---|---|
| Docker (binário) ❌ | Docker não instalado | Instalar [Docker Engine](https://docs.docker.com/engine/install/) ou [Docker Desktop](https://docs.docker.com/desktop/) |
| Docker (daemon) ❌ | Daemon parado | `sudo systemctl start docker` (Linux) ou abrir Docker Desktop |
| Docker (daemon) ❌ | Usuário sem permissão | `sudo usermod -aG docker $USER` e reabrir o terminal |
| Imagem mark2tex ⚠️ | Imagem não baixada | Executar `mark2tex` uma vez — a imagem é puxada automaticamente |
| Imagem mark2tex ⚠️ | Imagem corrompida | `docker rmi mark2tex:latest && mark2tex` |
| Pandoc ⚠️ | Não instalado no host | Ignorar — Pandoc está na imagem Docker |
| Python ❌ | Python < 3.10 | Instalar Python 3.10+ via [python.org](https://python.org) ou `pyenv` |
| Espaço em disco ⚠️ | < 2 GB livres | Liberar espaço; a imagem ocupa ~1,1 GB |

### 8.3 Usando `check` em scripts e CI

```bash
# Abortar se houver erros críticos
mark2tex check || { echo "Ambiente inválido — abortando."; exit 1; }

# Silencioso — apenas código de saída
mark2tex check > /dev/null 2>&1 && echo "OK" || echo "ERRO"
```

Código de saída `0` quando não há erros (pode haver avisos); `1` quando
pelo menos uma probe crítica falha.

---

## 9. Erros comuns do XeLaTeX — o que significam

O Mark2TeX traduz os logs do XeLaTeX para mensagens simples, mas quando
a compilação falha o log completo aparece no console da TUI. Esta tabela
ajuda a interpretar as mensagens mais frequentes.

| Mensagem no log | Causa | Solução |
|---|---|---|
| `Font ... not found` | Fonte declarada no YAML não existe na imagem | Usar um dos quatro valores válidos de `font` |
| `File '....sty' not found` | Pacote LaTeX ausente na imagem | Abrir issue no repositório para adicionar ao `Dockerfile` |
| `Undefined control sequence` | Comando LaTeX inválido no corpo do `.md` | Verificar blocos raw `{=latex}` por erros de digitação |
| `Missing $ inserted` | Símbolo matemático fora de `$...$` | Escapar o símbolo (`\$`) ou colocá-lo dentro de `$...$` |
| `Overfull \hbox` | Linha muito longa para a coluna | Aviso não crítico — o PDF é gerado mesmo assim |
| `I can't find file` | Imagem referenciada não existe no caminho informado | Verificar caminho e extensão do arquivo de imagem |
| `Citation ... undefined` | Chave BibTeX não encontrada no `.bib` | Verificar a chave no `.bib` e o campo `bibliography` no YAML |
| `Output loop --- too many` | Referências cruzadas em loop | Recompilar — quase sempre se resolve na segunda passagem |

### 9.1 Encontrando a causa raiz no log

1. Na TUI, role o console inferior até o final.
2. Procure pela primeira linha que começa com `!` — essa é a causa raiz.
3. As linhas seguintes começando com `l.NNN` indicam o número de linha no
   `.tex` gerado (útil para localizar o trecho no `.md` original).

---

## 10. Integração com CI/CD

### 10.1 GitHub Actions — gerar PDF a cada push

Crie `.github/workflows/build-pdf.yml`:

```yaml
name: Build PDF

on:
  push:
    paths:
      - 'docs/**.md'
      - 'referencias.bib'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Mark2TeX
        run: pip install mark2tex

      - name: Check environment
        run: mark2tex check

      - name: Build PDF
        run: |
          mark2tex compile docs/meu-tcc.md \
            --template tcc-abnt \
            --font liberation-serif

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documento-compilado
          path: docs/meu-tcc.pdf
          retention-days: 30
```

> O runner `ubuntu-latest` já tem Docker disponível.
> O passo `mark2tex check` retorna código `1` em caso de erro crítico,
> abortando o workflow antes da compilação.

### 10.2 GitLab CI

```yaml
build-pdf:
  image: python:3.12-slim
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
  before_script:
    - pip install mark2tex
    - mark2tex check
  script:
    - mark2tex compile docs/meu-tcc.md --template tcc-abnt
  artifacts:
    paths:
      - docs/meu-tcc.pdf
    expire_in: 1 week
```

### 10.3 Pre-commit hook local

Para compilar automaticamente antes de cada commit:

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
set -e
echo "[mark2tex] Verificando ambiente..."
mark2tex check || exit 1
echo "[mark2tex] Compilando documentação..."
mark2tex compile docs/meu-tcc.md --template tcc-abnt
git add docs/meu-tcc.pdf
```

Torne o hook executável:

```bash
chmod +x .git/hooks/pre-commit
```

# Manual de Uso — Mark2TeX

Este manual cobre **como escrever** documentos para o Mark2TeX: sintaxe Markdown suportada, inserção de imagens, tabelas, alertas, código, fórmulas e referências bibliográficas. Para instalação e execução, consulte o [README](../README.pt-BR.md).

---

## Índice

1. [Estrutura básica de um documento](#1-estrutura-básica-de-um-documento)
2. [Metadados YAML (frontmatter)](#2-metadados-yaml-frontmatter)
3. [Texto e parágrafos](#3-texto-e-parágrafos)
4. [Títulos e seções](#4-títulos-e-seções)
5. [Listas](#5-listas)
6. [Imagens](#6-imagens)
7. [Tabelas](#7-tabelas)
8. [Código](#8-código)
9. [Fórmulas matemáticas](#9-fórmulas-matemáticas)
10. [Caixas de destaque (alertas)](#10-caixas-de-destaque-alertas)
11. [Links e referências cruzadas](#11-links-e-referências-cruzadas)
12. [Bibliografia](#12-bibliografia)
13. [Fontes disponíveis](#13-fontes-disponíveis)
14. [Templates disponíveis](#14-templates-disponíveis)

---

## 1. Estrutura básica de um documento

Um arquivo `.md` para o Mark2TeX é composto por um bloco de metadados YAML no topo (opcional, mas recomendado) seguido do conteúdo em Markdown:

```markdown
---
title: Meu Documento
author: Fulano de Tal
date: 2026-05-04
template: doc-tecnica
---

## Introdução

Texto do documento aqui.
```

---

## 2. Metadados YAML (frontmatter)

O bloco entre `---` no início do arquivo configura o documento. Os campos variam por template, mas os mais comuns são:

```yaml
---
title: Título do Documento
subtitle: Subtítulo opcional
author:
  - name: Fulano de Tal
    affiliation: Universidade X
date: 2026-05-04
version: "1.0"
logo: assets/logo.png        # caminho relativo à pasta do .md
bibliography: referencias.bib
---
```

> **Dica:** Para o template `tcc`, campos como `orientador`, `curso` e `instituicao` também são suportados. Consulte os arquivos `examples/` para ver exemplos completos por template.

---

## 3. Texto e parágrafos

Em Markdown, **uma quebra de linha simples não cria um novo parágrafo**. Para iniciar um novo parágrafo, deixe uma linha em branco entre os blocos de texto:

```markdown
Este é o primeiro parágrafo. Ele pode continuar
nessa linha sem problema — ainda é o mesmo parágrafo.

Este é o segundo parágrafo, separado por uma linha em branco.
```

Para forçar uma quebra de linha dentro do mesmo parágrafo (sem criar um novo), termine a linha com **dois espaços** ou use uma barra invertida `\`:

```markdown
Primeira linha com dois espaços no final  
Segunda linha, mesmo parágrafo.
```

Formatação inline:

| Sintaxe | Resultado |
|---|---|
| `**negrito**` | **negrito** |
| `*itálico*` | *itálico* |
| `` `código inline` `` | `código inline` |
| `~~riscado~~` | ~~riscado~~ |

---

## 4. Títulos e seções

Use `#` para definir a hierarquia de seções. O número de `#` indica o nível:

```markdown
# Título principal (evite usar — o título já vem do frontmatter)
## Seção
### Subseção
#### Subsubseção
```

> **Atenção:** Não pule níveis (ex.: de `##` direto para `####`). Isso pode causar inconsistências no índice gerado automaticamente.

---

## 5. Listas

**Lista não ordenada:**

```markdown
- Primeiro item
- Segundo item
- Terceiro item
```

**Lista ordenada:**

```markdown
1. Primeiro passo
2. Segundo passo
3. Terceiro passo
```

**Lista aninhada** (use 2 ou 4 espaços de indentação):

```markdown
- Item principal
  - Subitem A
  - Subitem B
- Outro item principal
```

---

## 6. Imagens

A sintaxe padrão do Markdown para imagens funciona em todos os templates:

```markdown
![Texto alternativo](caminho/para/imagem.png)
```

### Redimensionando imagens

Para controlar o tamanho, use atributos Pandoc:

```markdown
![Legenda da imagem](imagem.png){ width=60% }
```

```markdown
![Legenda da imagem](imagem.png){ width=8cm }
```

### Centralizando imagens

O LaTeX centraliza imagens automaticamente quando a legenda está presente. Se quiser forçar centralização sem legenda:

```markdown
![](imagem.png){ width=50% }
```

### Referenciando imagens no texto

Para referenciar uma figura pelo número (ex.: "veja a Figura 1"), adicione um label:

```markdown
![Diagrama de arquitetura](arquitetura.png){ #fig:arq width=80% }

Como pode ser visto na @fig:arq, a arquitetura é composta por...
```

### Dicas práticas

- Prefira **caminhos relativos** ao arquivo `.md` (ex.: `imagens/logo.png`).
- Formatos suportados: PNG, JPEG, PDF, SVG (via conversão interna).
- Para imagens lado a lado, use uma tabela sem bordas com imagens nas células.

---

## 7. Tabelas

Sintaxe de tabela Markdown com cabeçalho:

```markdown
| Coluna A | Coluna B | Coluna C |
|----------|----------|----------|
| Dado 1   | Dado 2   | Dado 3   |
| Dado 4   | Dado 5   | Dado 6   |
```

**Alinhamento de colunas:**

```markdown
| Esquerda | Centro  | Direita |
|:---------|:-------:|--------:|
| texto    | texto   |   texto |
```

> **Dica:** Para tabelas longas que ocupam mais de uma página, o Mark2TeX usa `longtable` automaticamente via Pandoc.

---

## 8. Código

**Inline:** envolva com crases simples: `` `variavel` ``.

**Bloco de código com realce de sintaxe:**

````markdown
```python
def hello():
    print("Olá, Mundo!")
```
````

Linguagens suportadas para realce: `python`, `bash`, `javascript`, `typescript`, `java`, `c`, `cpp`, `go`, `rust`, `sql`, `json`, `yaml`, `latex`, entre outras.

---

## 9. Fórmulas matemáticas

**Inline** (dentro do parágrafo):

```markdown
A equação $E = mc^2$ foi proposta por Einstein.
```

**Bloco** (centralizado, em linha própria):

```markdown
$$
\int_{a}^{b} f(x)\,dx = F(b) - F(a)
$$
```

O motor XeLaTeX suporta toda a sintaxe LaTeX Math, incluindo os pacotes `amsmath` e `amssymb`.

---

## 10. Caixas de destaque (alertas)

Os templates Mark2TeX suportam caixas coloridas especiais via sintaxe de div fenced do Pandoc:

```markdown
::: infobox
Informação importante aqui.
:::

::: warningbox
Atenção: este passo é irreversível.
:::

::: dangerbox
Erro crítico: verifique a configuração antes de prosseguir.
:::

::: successbox
Operação concluída com sucesso!
:::

::: rulebox
Regra ou definição formal do documento.
:::
```

| Caixa | Cor | Uso recomendado |
|---|---|---|
| `infobox` | Teal | Notas, dicas, informações adicionais |
| `warningbox` | Âmbar | Avisos, cuidados, pontos de atenção |
| `dangerbox` | Vermelho | Erros, riscos, ações destrutivas |
| `successbox` | Verde | Confirmações, resultados esperados |
| `rulebox` | Cinza | Definições, regras, normas |

---

## 11. Links e referências cruzadas

**Link externo:**

```markdown
[Texto do link](https://exemplo.com)
```

**Link para seção do mesmo documento:**

```markdown
[Veja a seção de Imagens](#6-imagens)
```

**Referência bibliográfica no texto:**

```markdown
Como descrito em @silva2023, os resultados indicam...
```

---

## 12. Bibliografia

Crie um arquivo `referencias.bib` na mesma pasta do seu `.md`:

```bibtex
@article{silva2023,
  author  = {Silva, João},
  title   = {Título do Artigo},
  journal = {Nome do Periódico},
  year    = {2023},
  volume  = {10},
  pages   = {1--15},
}
```

No frontmatter YAML do seu `.md`, aponte para o arquivo:

```yaml
---
bibliography: referencias.bib
---
```

Cite no texto com `@chave` (narrativa) ou `[@chave]` (entre parênteses). O Mark2TeX processa as referências automaticamente via BibTeX quando o arquivo `.bib` está presente.

---

## 13. Fontes disponíveis

Passe a flag `--font` ao compilar pela TUI ou pela linha de comando:

| Flag | Fonte renderizada | Equivalente a |
|---|---|---|
| `--font arial` | Liberation Sans | Arial |
| `--font helvetica` | Nimbus Sans | Helvetica |
| `--font times` | Liberation Serif | Times New Roman |
| `--font ubuntu` | Ubuntu | — (padrão) |

Se nenhuma flag for passada, a fonte padrão é **Ubuntu**.

---

## 14. Templates disponíveis

| Template | Finalidade | Norma |
|---|---|---|
| `tcc` | Trabalho de Conclusão de Curso | ABNT |
| `artigo-ieee` | Artigo para conferência | IEEE |
| `doc-tecnica` | Documentação técnica interna | — |
| `projeto` | Proposta de projeto | — |
| `apresentacao` | Slides (Beamer) | — |

Para exemplos completos de cada template, consulte a pasta [`examples/`](../examples/).

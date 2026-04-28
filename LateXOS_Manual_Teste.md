---
title: Manual de Operação e Guia de Referência LateXOS
author: Hylbert Rodrigues
institution: Ecossistema de Automação Acadêmica
campus: Virtual Campus
department: Desenvolvimento de Ferramentas
course: Engenharia de Software
advisor: Automação
coadvisor: Produtividade
city: Mundo Digital
year: "2026"
acknowledgments: Agradecemos a todos os estudantes que buscam simplificar a formatação de seus trabalhos acadêmicos.
abstract-pt: Este documento serve como manual de usuário e prova de conceito para a ferramenta LateXOS. Ele demonstra a capacidade de conversão de Markdown para PDF seguindo as normas ABNT, validando a instalação do ambiente Docker e do motor XeLaTeX.
abstract-en: This document serves as a user manual and proof of concept for the LateXOS tool. It demonstrates the ability to convert Markdown to PDF following ABNT standards, validating the Docker environment and XeLaTeX engine installation.
siglas: \begin{description} \item[ABNT] Associação Brasileira de Normas Técnicas \item[PDF] Portable Document Format \item[YAML] Yet Another Markup Language \item[TCC] Trabalho de Conclusão de Curso \end{description}
simbolos: \begin{description} \item[$\rightarrow$] Direcionamento de fluxo \item[$\sum$] Somatório de elementos \item[$\alpha$] Coeficiente de aprendizado \end{description}
bibliography: referencias.bib
---

# Introdução ao LateXOS

O **LateXOS** é um sistema de automação de documentos acadêmicos que desacopla o conteúdo da formatação. Em vez de lutar com a sintaxe complexa do LaTeX, o usuário escreve em **Markdown**, e a ferramenta cuida de toda a burocracia da norma ABNT através de um pipeline Dockerizado.

## O Fluxo de Trabalho
O processo segue a seguinte cadeia:
**Markdown** $\rightarrow$ **Pandoc** $\rightarrow$ **XeLaTeX** $\rightarrow$ **PDF**

Isso garante que qualquer pessoa com Docker instalado consiga gerar o mesmo PDF, sem precisar instalar gigabytes de distribuições TeX localmente.

# Guia de Operação (Comandos)

Para operar a ferramenta, utilize os seguintes comandos no terminal dentro da pasta `LateXOS`:

## Preparando o Ambiente
Se for a primeira vez utilizando a ferramenta ou se o `Dockerfile` foi alterado:
`make build-image`

*   **O que faz**: Baixa a imagem base, instala o Pandoc, as fontes da Microsoft, a distribuição TeX Live e as bibliotecas de idioma.

## Gerando o PDF (Manual)
Para compilar um arquivo específico:
`make compile INPUT=nome_do_arquivo.md TEMPLATE=tcc`

*   **INPUT**: O arquivo Markdown que contém seu texto.
*   **TEMPLATE**: O modelo a ser usado (ex: `tcc`).

## Modo Tempo Real (Auto-compile)
Para não precisar digitar o comando a cada alteração:
`./watch.sh nome_do_arquivo.md`

*   **O que faz**: Monitora o arquivo. Sempre que você salvar no Obsidian, o PDF é atualizado automaticamente.

# Anatomia do Arquivo Markdown

O segredo do LateXOS está no cabeçalho **YAML**, localizado no topo do arquivo entre dois conjuntos de `---`.

## Campos Principais
- `title`: Título do trabalho (aparece na capa e folha de rosto).
- `author`: Seu nome completo.
- `institution`/`campus`/`department`: Dados institucionais para o cabeçalho da capa.
- `siglas`: Lista de abreviaturas usando o ambiente `description` do LaTeX.
- `simbolos`: Lista de símbolos matemáticos.

**Dica Importante**: Sempre utilize aspas simples (`' '`) ao envolver comandos LaTeX no YAML para evitar erros de escape.

# Galeria de Recursos (Demonstração)

Esta seção prova que a ferramenta está funcionando corretamente.

## Matemática e Fórmulas
O LateXOS suporta matemática completa. Podemos ter fórmulas inline como $E = mc^2$ ou fórmulas em bloco:

$$
\int_{a}^{b} f(x) \,dx = F(b) - F(a)
$$

## Código e Programação
Blocos de código são formatados com fontes monoespaçadas e realce de sintaxe. Exemplo em Python:

```python
def saudacao(nome):
    print(f"Olá, {nome}! Bem-vindo ao LateXOS.")

saudacao("Usuário")
```

## Formatação de Texto
- **Negrito** para ênfase.
- *Itálico* para termos estrangeiros.
- Listas com bullets:
    - Item A
    - Item B
- Listas numeradas:
    1. Primeiro passo
    2. Segundo passo

## Citações e Bibliografia
As citações são feitas via BibTeX. Ao usar o comando `\cite{chave}`, o sistema busca a referência no arquivo `.bib` e gera a lista final automaticamente seguindo a norma ABNT.

# Conclusões do Teste

Se você está lendo este PDF, significa que:

1. O Docker está configurado corretamente.
2. As fontes Times New Roman foram instaladas.
3. O motor XeLaTeX está processando o Markdown via Pandoc.
4. A norma ABNT está sendo aplicada.

Tudo pronto para começar seu TCC!

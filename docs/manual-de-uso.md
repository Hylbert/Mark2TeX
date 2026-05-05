# Manual de Uso — Mark2TeX

## Índice

1. [Instalação](#instalação)
2. [Comandos CLI](#comandos-cli)
3. [Diagnóstico do Sistema (`mark2tex check`)](#diagnóstico-do-sistema)
4. [Usando a TUI](#usando-a-tui)
5. [Anatomia do arquivo Markdown](#anatomia-do-arquivo-markdown)
6. [Templates disponíveis](#templates-disponíveis)

---

## Instalação

```bash
# Requer Python 3.10+ e Docker instalado e em execução
pipx install mark2tex
```

Após instalar, verifique o ambiente:

```bash
mark2tex check
```

---

## Comandos CLI

| Comando | Descrição |
|---|---|
| `mark2tex` | Abre a TUI interativa (padrão) |
| `mark2tex check` | Diagnóstico completo do sistema |
| `mark2tex init [--template NOME]` | Copia template + exemplo para o diretório atual |
| `mark2tex uninstall` | Remove imagem Docker e assets |
| `mark2tex doctor` | Alias depreciado para `check` |

---

## Diagnóstico do Sistema

O comando `mark2tex check` executa seis verificações e exibe um relatório visual no terminal.

### Verificações realizadas

| Verificação | O que analisa | Severidade se falhar |
|---|---|---|
| **Mark2TeX** | Versão instalada do pacote | Aviso |
| **Docker (binário)** | Se `docker` está disponível no PATH | Erro crítico |
| **Docker (daemon)** | Se o daemon Docker está ativo e acessível | Erro crítico |
| **Imagem mark2tex** | Se `mark2tex:latest` existe localmente | Aviso |
| **Pandoc** | Se pandoc está instalado no host (opcional) | Aviso |
| **Python** | Versão do Python (mínimo 3.10) | Erro crítico |
| **Espaço em disco** | Espaço livre, usado e total + footprint da imagem | Aviso |

### Interpretando o resultado

```
✅  Tudo certo! Mark2TeX está pronto para uso.
```
Nenhum erro e nenhum aviso — pode compilar.

```
⚠️  Verifique os avisos acima antes de compilar.
```
Há avisos (ex: pandoc não encontrado, imagem não baixada ainda). A ferramenta pode funcionar, mas revise.

```
❌  Corrija os itens marcados com ❌ antes de compilar.
```
Há erros críticos (Docker não encontrado, daemon parado, Python incompatível). A compilação não funcionará.

### Códigos de saída

| Código | Significado |
|---|---|
| `0` | Nenhum erro (pode haver avisos) |
| `1` | Pelo menos um erro crítico |

Isso permite usar `mark2tex check` em scripts e pipelines CI:

```bash
mark2tex check && echo "Ambiente OK" || echo "Corrija os erros acima"
```

---

## Usando a TUI

Execute `mark2tex` em qualquer diretório com arquivos `.md`:

```bash
cd ~/meus-documentos
mark2tex
```

### Fluxo básico

1. **Painel esquerdo** — selecione o arquivo `.md` a compilar
2. **Painel central (Templates)** — escolha o template desejado
3. **Painel central (Fontes)** — opcionalmente escolha a fonte
4. Pressione **`c`** ou clique em **COMPILAR**
5. Acompanhe o progresso no console inferior

### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `c` | Compilar documento selecionado |
| `w` | Ativar/desativar Watch Mode |
| `F1` / `?` | Tela de ajuda |
| `Esc` / `q` | Menu global (Ajustes, Ajuda, Sair) |
| `Tab` | Navegar entre painéis |
| `↑` `↓` | Navegar nas listas |

### Watch Mode

O Watch Mode monitora o arquivo selecionado e recompila automaticamente a cada vez que ele é salvo. Ideal para ciclos rápidos de edição.

---

## Anatomia do arquivo Markdown

O Mark2TeX usa um cabeçalho **YAML** no topo do arquivo para configurar a compilação:

```markdown
---
title: "Meu Trabalho"
author: "Seu Nome"
date: "2026-05-05"
template: tcc-abnt
lang: pt-BR
bibliography: referencias.bib
---

# Introdução

Conteúdo do documento...
```

### Campos principais

| Campo | Descrição | Obrigatório |
|---|---|---|
| `title` | Título do documento | Sim |
| `author` | Nome do autor | Sim |
| `date` | Data (YYYY-MM-DD) | Recomendado |
| `template` | Nome do template a usar | Sim |
| `lang` | Idioma (`pt-BR`, `en`) | Recomendado |
| `bibliography` | Caminho para arquivo `.bib` | Não |

---

## Templates disponíveis

| Template | Finalidade | Norma |
|---|---|---|
| `tcc-abnt` | Trabalho de Conclusão de Curso | ABNT |
| `artigo-ieee` | Artigo para conferência IEEE | IEEE |
| `artigo-abnt` | Artigo acadêmico | ABNT |
| `doc-tecnica` | Documentação técnica | — |
| `projeto` | Proposta de projeto | — |

Cada template possui um arquivo de exemplo em `mark2tex/templates/<nome>/exemplo.md`.

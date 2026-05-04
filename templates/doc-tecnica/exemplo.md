---
# =============================================================
# METADADOS OBRIGATÓRIOS
# =============================================================
title: "Título da Documentação"
subtitle: "Subtítulo ou versão do documento"  # opcional

author:
  - name: "Nome do Autor"
  # - name: "Nome do Segundo Autor"

date: "Maio 2026"   # ou use year: "2026"
version: "1.0.0"    # aparece na capa como v1.0.0

# =============================================================
# ASSETS  —  mesma pasta que este .md (ou subpastas)
# =============================================================
#
#   meu-projeto/
#   ├── documento.md
#   ├── logo.png            ← logo: "logo.png"
#   └── figuras/
#       └── arquitetura.png  ← ![Legenda](figuras/arquitetura.png)
#
# logo na capa (opcional — remova para exibir "Mark2TeX" como texto)
logo: "logo.png"

# =============================================================
# PÁGINAS ESPECIAIS (todas opcionais — remova para omitir)
# =============================================================

# Aviso legal / confidencialidade
confidentiality: |
  Documento confidencial. Não é permitido copiar, reproduzir ou divulgar
  este documento sem autorização expressa.\\
  Cidade, UF — 2026.

# Sobre (empresa/time)
about-title: "Sobre o Projeto"
about: |
  Breve descrição do contexto, equipe ou organização responsável pelo documento.

# Introdução / préfacio
preface-title: "Olá, seja bem-vindo(a)!"
preface: |
  Este documento foi preparado para guiar o leitor no uso e compreensão
  do sistema descrito nas seções a seguir.

# Título do índice
toc-title: "Índice"

# Página final
closing-title: "Obrigado!"
closing: |
  Este documento foi elaborado pela equipe responsável pelo projeto.
  Para dúvidas ou sugestões, entre em contato.
---

# Visão Geral

Descreva aqui o objetivo do sistema ou documento.

::: infobox
**Principais Funcionalidades**

- **Funcionalidade A** --- descrição breve.
- **Funcionalidade B** --- descrição breve.
:::

# Arquitetura

## Visão de Alto Nível

| Serviço | Responsabilidade |
|---|---|
| **Serviço A** | Descrição |
| **Serviço B** | Descrição |

## Fluxo de Dados

::: rulebox
**Pipeline**

1. Etapa 1
2. Etapa 2
3. Etapa 3
:::

## Diagrama

![Arquitetura do sistema](figuras/arquitetura.png)

# Instalação

## Pré-requisitos

- Docker 20.10+
- Python 3.10+

## Passos

```bash
git clone <repository-url>
cd meu-projeto
docker-compose up -d
```

# API REST

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/status` | Health check |
| `POST` | `/recurso` | Cria recurso |

# Troubleshooting

::: dangerbox
**"Erro X"**\
Descrição e como resolver.
:::

::: warningbox
**"Aviso Y"**\
Descrição e como resolver.
:::

::: successbox
**Tudo certo!**\
Mensagem de sucesso ou dica positiva.
:::

# FAQ

**P: Pergunta frequente?**\
R: Resposta objetiva.

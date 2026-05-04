---
title: "Título da Documentação"
subtitle: "Subtítulo ou versão do documento"

author:
  - name: "Nome do Autor"

date: "Maio 2026"
version: "1.0.0"

# =============================================================
# ASSETS  —  mesma pasta que este .md (ou subpastas)
# =============================================================
#
#   meu-projeto/
#   ├── documento.md
#   ├── logo.png            ← descomente logo: abaixo
#   └── figuras/
#       └── arquitetura.png  ← ![Legenda](figuras/arquitetura.png)

# logo na capa (descomente se tiver o arquivo)
# logo: "logo.png"

# =============================================================
# PÁGINAS ESPECIAIS (todas opcionais — remova para omitir)
# =============================================================

confidentiality: |
  Documento confidencial. Não é permitido copiar, reproduzir ou divulgar
  este documento sem autorização expressa.\\
  Cidade, UF — 2026.

about-title: "Sobre o Projeto"
about: |
  Breve descrição do contexto, equipe ou organização responsável pelo documento.

preface-title: "Olá, seja bem-vindo(a)!"
preface: |
  Este documento foi preparado para guiar o leitor no uso e compreensão
  do sistema descrito nas seções a seguir.

toc-title: "Índice"

closing-title: "Obrigado!"
closing: |
  Este documento foi elaborado pela equipe responsável pelo projeto.
  Para dúvidas ou sugestões, entre em contato.
---

# Visão Geral

Descreva aqui o objetivo do sistema ou documento.

# Arquitetura

## Visão de Alto Nível

| Serviço | Responsabilidade |
|---|---|
| **Serviço A** | Descrição |
| **Serviço B** | Descrição |

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

# FAQ

**P: Pergunta frequente?**\
R: Resposta objetiva.

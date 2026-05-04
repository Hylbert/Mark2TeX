---
# =============================================================
# METADADOS OBRIGATÓRIOS
# =============================================================
title: "Título do Trabalho de Conclusão de Curso"
# subtitle: "Subtítulo, se houver"

author:
  - name: "Nome Completo do Autor"
  # - name: "Nome do Segundo Autor"

year: "2026"
city: "Cidade"
state: "UF"
lang: "portuguese"

# =============================================================
# FONTE  —  escolha a tipografia do documento
# =============================================================
#
# Valores aceitos:
#   times       → Liberation Serif  (métricas idênticas à Times New Roman) [ABNT NBR 14724 — padrão]
#   arial       → Liberation Sans   (métricas pixel-a-pixel idênticas à Arial)  [ABNT NBR 14724 — aceito]
#   helvetica   → Nimbus Sans       (Helvetica livre, URW)
#   ubuntu-sans → Ubuntu Sans       (fonte da doc. técnica Mark2TeX)
#
# Padrão: times (Liberation Serif)
# font: "times"

# =============================================================
# DADOS INSTITUCIONAIS
# =============================================================
institution: "Nome da Instituição de Ensino"
campus: "Nome do Campus"             # opcional
department: "Nome do Departamento"   # opcional
course: "Nome do Curso"
degree: "Bacharel em Nome do Curso"
# nature: "Trabalho de Conclusão de Curso apresentado..."  # texto customizado
area: "Nome da Área de Concentração"  # opcional

# =============================================================
# ORIENTAÇÃO
# =============================================================
advisor: "Prof. Dr. Nome do Orientador"
# advisor-label: "Orientador(a)"
# coadvisor: "Prof. Dr. Nome do Coorientador"

# =============================================================
# ASSETS  —  imagens, logo e arquivos de suporte
# =============================================================
#
# REGRA: todos os arquivos devem estar na MESMA PASTA que este .md
# (ou em subpastas dentro dela). Caminhos relativos são aceitos.
#
# Estrutura recomendada:
#
#   meu-tcc/
#   ├── meu-tcc.md
#   ├── referencias.bib
#   ├── logo.png              ← descomente logo: abaixo
#   ├── ficha-catalografica.png
#   └── figuras/
#       └── minha-figura.png  ← ![Legenda](figuras/minha-figura.png)
#
# Arquivos fora desta pasta NÃO são visíveis durante a compilação.

# Logo na capa (descomente e ajuste o caminho se tiver o arquivo)
# logo: "logo.png"
# logo-width: "0.12"   # fração de \textwidth (0.12 ≈ 1,8 cm)

# Ficha catalográfica (descomente se tiver a imagem fornecida pela biblioteca)
# catalog-image: "ficha-catalografica.png"

# =============================================================
# FOLHA DE APROVAÇÃO  (remova o bloco inteiro para omitir)
# =============================================================
approval-date: "DD de mês de 2026"
committee:
  - name: "Nome do Orientador"
    title: "Prof. Dr."
    institution: "Instituição"
  - name: "Nome do Membro 2"
    title: "Prof. Dr."
    institution: "Instituição"
  - name: "Nome do Membro 3"
    title: "Prof. Dr."
    institution: "Instituição"

# =============================================================
# ELEMENTOS PRÉ-TEXTUAIS OPCIONAIS
# =============================================================

dedication: "Aos meus familiares e amigos, pelo apoio constante."

acknowledgements: |
  À minha família, pelo incentivo em todos os momentos.
  Ao orientador, pela paciência e dedicação.

epigraph: "A educação é a arma mais poderosa que você pode usar para mudar o mundo."
epigraph-author: "Nelson Mandela"

abstract-pt: |
  Este trabalho apresenta... [resumo em português, 150 a 500 palavras].
keywords-pt: "palavra-chave 1; palavra-chave 2; palavra-chave 3"

abstract-en: |
  This work presents... [abstract in English].
keywords-en: "keyword 1; keyword 2; keyword 3"

list-of-figures: true
list-of-tables: true

abbreviations:
  - key: "ABNT"
    value: "Associação Brasileira de Normas Técnicas"
  - key: "TCC"
    value: "Trabalho de Conclusão de Curso"

symbols:
  - key: "$\\alpha$"
    value: "Coeficiente de aprendizado"
  - key: "$\\beta$"
    value: "Taxa de erro"

# =============================================================
# REFERÊNCIAS  (descomente se tiver o arquivo .bib na mesma pasta)
# =============================================================
# bibliography: "referencias"
---

# Introdução

Apresente aqui o tema, a delimitação, o objetivo geral, os objetivos específicos,
a justificativa e a metodologia. Evite citações diretas na introdução.

# Revisão de Literatura

Conteúdo da revisão bibliográfica.

# Metodologia

Descreva os materiais e métodos utilizados.

# Resultados e Discussão

Apresente e discuta os resultados obtidos.

# Conclusão

Síntese dos resultados. Sugira trabalhos futuros.

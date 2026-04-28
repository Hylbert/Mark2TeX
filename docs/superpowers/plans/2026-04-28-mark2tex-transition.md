# Mark2TeX Transition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition project from Mark2TeX to Mark2TeX, restructure files for professional distribution, and initialize a Git repository with strict governance.

**Architecture:** 
1. Initialize Git and create remote repository using `gh`.
2. Apply global renaming from `Mark2TeX` to `Mark2TeX`.
3. Reorganize files into a functional hierarchy (`bin/`, `examples/`, `docs/`).
4. Create base distribution files (`README.md`, `.gitignore`).
5. Establish GitFlow branching (`main` and `develop`).

**Tech Stack:** Git, GitHub CLI (`gh`), Bash, Makefile, Docker.

---

### Task 1: Git Initialization and Remote Setup

**Files:**
- Create: `.git/` (via git init)

- [ ] **Step 1: Initialize local git repository**
```bash
git init
```

- [ ] **Step 2: Create remote repository via gh CLI**
Run: `gh repo create Mark2TeX --public --source=. --remote=origin`
*Note: Follow interactive prompts to confirm creation.*

- [ ] **Step 3: Commit initial state (as a baseline)**
```bash
git add .
git commit -m "chore: commit inicial do projeto Mark2TeX antes da transição"
```

- [ ] **Step 4: Push to main**
```bash
git branch -M main
git push -u origin main
```

### Task 2: Global Renaming (Mark2TeX $\rightarrow$ Mark2TeX)

**Files:**
- Modify: All files and directory names

- [ ] **Step 1: Rename directory if applicable**
(If the root folder is named Mark2TeX, rename it to Mark2TeX)

- [ ] **Step 2: Replace text in all files**
Run: `grep -rl "Mark2TeX" . | xargs sed -i 's/Mark2TeX/Mark2TeX/g'`
Run: `grep -rl "mark2tex" . | xargs sed -i 's/mark2tex/mark2tex/g'`

- [ ] **Step 3: Rename files containing Mark2TeX**
Run: `find . -name "*Mark2TeX*" -exec bash -c 'mv "$1" "${1//Mark2TeX/Mark2TeX}"' _ {} \;`

- [ ] **Step 4: Commit renaming**
```bash
git add .
git commit -m "style: renomeia Mark2TeX para Mark2TeX em todo o projeto"
```

### Task 3: Professional Restructuring (Option A)

**Files:**
- Create: `bin/`, `examples/`, `docs/`
- Move: `scripts/build.sh` $\rightarrow$ `bin/build.sh`
- Move: `watch.sh` $\rightarrow$ `bin/watch.sh`
- Move: `template_*.md` $\rightarrow$ `examples/*.md`
- Move: `Mark2TeX_Manual_Teste.md` (now `Mark2TeX_Manual_Teste.md`) $\rightarrow$ `docs/manual.md`

- [ ] **Step 1: Create new directory structure**
```bash
mkdir -p bin examples docs
```

- [ ] **Step 2: Move binaries and scripts**
```bash
mv scripts/build.sh bin/build.sh
mv watch.sh bin/watch.sh
rmdir scripts
```

- [ ] **Step 3: Move example boilerplates**
```bash
mv template_tcc.md examples/tcc.md
mv template_artigo.md examples/artigo.md
mv template_projeto.md examples/projeto.md
```

- [ ] **Step 4: Move and rename manual**
```bash
mv Mark2TeX_Manual_Teste.md docs/manual.md
```

- [ ] **Step 5: Update Makefile paths**
Modify `Makefile` to point to `bin/build.sh` instead of `scripts/build.sh`.
```makefile
# Example change in Makefile
compile:
	docker run ... bin/build.sh ...
```

- [ ] **Step 6: Commit restructuring**
```bash
git add .
git commit -m "refactor: reestrutura pastas para layout profissional (Opção A)"
```

### Task 4: Base Distribution Files

**Files:**
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: Create .gitignore**
```bash
cat <<EOF > .gitignore
*.aux
*.log
*.out
*.toc
*.pdf
*.gz
.DS_Store
EOF
```

- [ ] **Step 2: Create README.md (in Portuguese)**
```markdown
# Mark2TeX

Ferramenta de automação para documentos acadêmicos que desacopla o conteúdo (Markdown) da formatação (LaTeX/ABNT).

## 🚀 Início Rápido

### Pré-requisitos
- Docker instalado

### Instalação e Uso
1. Clone o repositório: \`git clone ...\`
2. Construa a imagem: \`make build-image\`
3. Compile seu documento: \`make compile TEMPLATE=tcc INPUT=meu_arquivo.md\`

## 📂 Estrutura
- \`bin/\`: Scripts de execução.
- \`templates/\`: Modelos LaTeX.
- \`examples/\`: Modelos de Markdown.
- \`docs/\`: Manual detalhado.
```

- [ ] **Step 3: Commit base files**
```bash
git add .gitignore README.md
git commit -m "docs: adiciona README e .gitignore"
```

### Task 5: GitFlow Establishment

**Files:**
- Create: `develop` branch

- [ ] **Step 1: Create and push develop branch**
```bash
git checkout -b develop
git push -u origin develop
```

- [ ] **Step 2: Final verification**
Run: `git branch -a`
Expected: `main` and `develop` branches exist.

- [ ] **Step 3: Commit final setup**
```bash
git commit -m "chore: estabelece fluxo GitFlow com ramo develop"
```

# Guia de Contribuição do Mark2TeX

Estamos muito felizes com o seu interesse em contribuir para o Mark2TeX! 🚀 Antes de enviar sua contribuição, por favor, reserve um momento para ler as seguintes diretrizes.

- [Filosofia](#filosofia)
- [Diretrizes para Reporte de Issues](#diretrizes-para-reporte-de-issues)
- [Diretrizes para Pull Requests](#diretrizes-para-pull-requests)
- [Início Rápido](#início-rápido)

## Filosofia

🔑 Nossa filosofia é manter as coisas limpas, simples e minimalistas. 
O Mark2TeX busca remover a fricção entre a ideia e o documento final. Queremos que as melhorias alinhem-se a essa simplicidade: a ferramenta deve ser poderosa nos bastidores, mas invisível e intuitiva para o usuário.

## Diretrizes para Reporte de Issues

Por favor, pesquise por issues semelhantes antes de abrir uma nova e utilize sempre o template de issue disponível. Se encontrar um bug ou tiver uma sugestão de funcionalidade, descreva detalhadamente o cenário, a versão do Docker utilizada e, se possível, anexe um exemplo do arquivo Markdown que causou o problema.

## Diretrizes para Pull Requests

**Em *todos* os Pull Requests:** forneça uma descrição detalhada do problema resolvido ou da funcionalidade adicionada.

Antes de submeter seu PR, certifique-se de que:

- O PR foi enviado diretamente para a branch `develop`.
- O merge final deve ser realizado obrigatoriamente utilizando a flag `--no-ff` para preservar o histórico de branches.
- Você referenciou a issue relacionada no comentário do PR.
- A documentação em `docs/` ou no `README.md` foi atualizada para refletir a mudança.
- Todos os testes de compilação passam (o PDF é gerado sem erros).
- O código segue as boas práticas de programação e está limpo.

### Se você adicionar uma nova funcionalidade:

- Abra primeiro uma issue de sugestão para discutirmos a implementação.
- Forneça a justificativa do porquê essa funcionalidade é útil para o usuário.
- Submeta seu PR após a concordância dos mantenedores.

### Se você corrigir um bug:

- Se estiver resolvendo uma issue específica, adicione `fix: #<número da issue> <mensagem curta>` no título do seu PR (ex: `fix: #12 corrige erro de codificação de caracteres`).
- Forneça uma descrição detalhada do bug e como a correção o resolve.

### Por onde começar?

Uma ótima maneira de começar é procurar issues com as etiquetas `bug`, `help wanted` ou `feature request`. Issues marcadas como `good first issue` são ideais para novos contribuidores. Para mudanças maiores, discuta a solução primeiro; para mudanças pequenas, você pode abrir o PR diretamente.

## Início Rápido

1. Faça um **Fork** do repositório.
2. Clone seu fork: `git clone git@github.com:<seu-usuario>/Mark2TeX.git`
3. Crie uma branch de feature: `git checkout -b feature/nome-da-feature`
4. Implemente as mudanças e faça o push da sua branch.
5. Crie um Pull Request contra a branch `develop` descrevendo suas alterações.

**Sincronizando seu PR:**

Se houver conflitos ou se quiser atualizar sua branch local:
1. `git fetch upstream`
2. `git rebase upstream/develop`
3. Resolva os conflitos e faça o force push: `git push -f`

---
Agradecemos seu tempo e esforço para tornar o Mark2TeX melhor para todos!

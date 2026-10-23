# Instruções do workspace

## Conteúdo de `agents/`

`agents/skills/aws-architecture-diagrams/` contém a skill `aws-architecture-diagrams`, aplicável a tarefas de criação, edição, revisão e validação de diagramas de arquitetura AWS em draw.io e Mermaid. Consulte [SKILL.md](agents/skills/aws-architecture-diagrams/SKILL.md) antes de trabalhar nessas tarefas e siga o fluxo e os critérios de conclusão descritos nela.

Materiais de apoio da skill:

- [drawio-conventions.md](agents/skills/aws-architecture-diagrams/references/drawio-conventions.md): preservação de arquivos existentes, ícones oficiais AWS, layout, rótulos, conexões, integridade XML e inspeção visual.
- [mermaid-patterns.md](agents/skills/aws-architecture-diagrams/references/mermaid-patterns.md): padrões de sequência para fluxos, ramificações, retries, DLQ, recuperação e isolamento de consumidores.
- [aws-architecture-checklist.md](agents/skills/aws-architecture-diagrams/references/aws-architecture-checklist.md): checklist de semântica, confiabilidade, filas, idempotência, snapshots, TTL, segurança, observabilidade e revisão visual.
- [validate_drawio.py](agents/skills/aws-architecture-diagrams/scripts/validate_drawio.py): validador estrutural de arquivos draw.io/XML, incluindo referências, IDs, páginas, estilos e avisos de convenções.

Use os nomes e caminhos dos arquivos que existem acima; eles correspondem às referências citadas na skill.

## Regras para tarefas de diagramas AWS

- Entenda o estado atual e o objetivo do diagrama antes de editar. Releia o arquivo imediatamente antes de cada lote de alterações e preserve conteúdo, IDs, estilos, páginas e mudanças recentes do usuário sempre que possível.
- Não invente componentes, contratos, garantias ou decisões arquiteturais. Diferencie claramente o estado atual de propostas e sinalize escolhas ainda não aprovadas.
- Priorize a verdade arquitetural: toda seta deve representar uma interação real e indicar direção e semântica corretas. Não represente um datastore encaminhando eventos sem um mecanismo explícito; separe persistência e publicação quando forem operações distintas.
- Use draw.io para a topologia de infraestrutura e Mermaid, especialmente `sequenceDiagram`, para interações temporais, retries, falhas, DLQ, redrive e recuperação. Mantenha contratos, modelos de dados, premissas e decisões detalhadas em Markdown.
- Em draw.io, prefira ícones AWS oficiais compatíveis com o arquivo, mantenha limites de nuvem/conta corretos e use rótulos concisos no idioma do usuário. Preserve o estilo existente e evite substituir conteúdo editável por imagens.
- Revise aspectos aplicáveis de idempotência, falhas entre gravação e publicação, retenção de filas/DLQs e snapshots, TTL versus janela de replay, ordenação, limites de payload, isolamento de consumidores, segurança, operação e observabilidade. Não adicione componentes para resolver preocupações sem aprovação.
- Valide a estrutura e, quando as ferramentas estiverem disponíveis, exporte e inspecione visualmente todas as páginas relevantes. O validador não substitui a revisão semântica nem a inspeção visual.

Para validar um arquivo draw.io a partir da raiz do workspace:

```bash
python agents/skills/aws-architecture-diagrams/scripts/validate_drawio.py <arquivo.drawio-ou-xml>
```

O validador também aceita `--page` (índice baseado em zero ou nome exato da página), `--strict-mx` e `--json`. Relate limitações quando não for possível renderizar ou inspecionar visualmente o resultado.
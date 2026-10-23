---
name: aws-architecture-diagrams

description: Create, edit, review, and validate clear AWS architecture diagrams in draw.io and Mermaid. Use for AWS infrastructure drawings, architecture proposals, webhook and event-driven integrations, queues and DLQs, serverless systems, architecture reviews, diagram cleanup, or when visual communication must follow AWS iconography and correct synchronous/asynchronous semantics.
---

# AWS Architecture Diagrams

Create architecture artifacts that are technically truthful, visually clear, safe to edit, and suitable for review by architects. Architecture semantics come before visual polish. Visible text must read like it was written for the diagram's audience, not copied from code, infrastructure configuration, or an AI-generated draft.

Resolve bundled `references/` and `scripts/` paths relative to the actual source directory of this `SKILL.md`, never relative to the current project.

## Non-negotiable principles

1. Inspect an existing drawing before changing it. Evolve it rather than recreating it unless a rebuild is explicitly justified.
2. Re-read the source immediately before editing because the user may have changed it in draw.io during the session.
3. Never overwrite or normalize away recent user changes.
4. Use official AWS architecture icons already compatible with the drawing. Do not improvise service icons or represent AWS services with generic boxes.
5. Make every arrow describe a real communication. Never connect components merely to imply visual order.
6. Keep the main infrastructure drawing concise. Put temporal behavior, retries, branches, and recovery details in Mermaid sequence diagrams unless the user asks otherwise.
7. Mark unapproved choices in plain language, such as `Proposes x` or `x validation`. Do not use opaque codes such as `TBD`, `TODO`, or `Decision point` badges that require a separate key.
8. Do not invent services, endpoints, contracts, guarantees, or business behavior. Ask when the choice changes the architecture.
9. Preserve the user's language for editorial labels and preserve technical identifiers exactly.
10. A diagram is complete only after structural validation, a human-readability pass, and visual inspection of a rendered export.

## Required workflow

### 1. Establish scope and truth status
Identify:
* current state versus proposed state;
* intended audience and review objective;
* required deliverables: draw.io, Mermaid, Markdown, image, or PDF;
* components and names that already exist;
* decisions that remain open;
* whether the drawing is infrastructure-only or also contains behavior.

Do not present a proposal as an approved design.

### 2. Inspect the source
For draw.io/XML:
* locate every relevant file;
* identify whether it is a bare `mxGraphModel`, an uncompressed `mxfile`, or compressed draw.io content;
* enumerate pages, cells, AWS shapes, labels, edges, parents, geometry, and styles;
* identify embedded images, generic shapes, orphan references, duplicated IDs, and user-object wrappers;
* detect mixed AWS icon generations and hidden or zero-size cells carrying encoded or unexpectedly long content;
* inspect neighboring components before creating new ones so styles are inherited rather than guessed.

For Mermaid or Markdown, read the complete relevant blocks before editing.

### 3. Review the architecture before layout
For every connection, state internally:
* who initiates it;
* protocol or interaction type;
* synchronous or asynchronous behavior;
* payload versus reference;
* success acknowledgement;
* retry owner;
* failure destination;
* ordering and idempotency assumptions.

Correct architectural ambiguity before publishing the diagram. A datastore must not appear to forward an event unless a real mechanism such as a stream is explicitly part of the design.

Example of correct dual-operation semantics:
```
Hydrator
1. PutItem snapshot -> DynamoDB
2. PutEvents reference -> EventBridge
```

Do not draw `Hydrator -> DynamoDB -> EventBridge` unless DynamoDB actually triggers the publication path.

### 4. Design the information hierarchy
Default separation:
* `draw.io`: principal infrastructure and trust/account boundaries;
* `Mermaid`: `sequenceDiagram`: happy path, retries, race conditions, DLQ, redrive, and recovery;
* `Markdown`: event contracts, data models, assumptions, decisions, and change lists.

Prefer one purpose per page. Do not combine infrastructure, multiple failure scenarios, and long decision lists on one canvas. Use one primary flow per horizontal lane. If a page includes a secondary flow, such as an internal query path beneath an event ingestion path, give it a short heading and enough whitespace to read independently. Do not route optional or unresolved flows around the edge of the canvas merely to keep them visible; move them to a concise decision note or the supporting Markdown.

### 5. Edit safely
* Prefer targeted edits over replacement.
* Preserve existing IDs, styles, page names, account boundaries, and component names where possible.
* Keep service components as official AWS shapes.
* Use unbiased text only for short titles, legends, and decision markers.
* Attach short technical details to the relevant component or edge.
* Avoid placing explanatory paragraphs in the infrastructure canvas.
* Keep generated helper and validation artifacts outside the project unless the user requests them.

### 6. Apply the visual conventions
Read `references/drawio-conventions.md` for the complete conventions.

Core rules:
* primary flow reads left to right;
* account and cloud boundaries remain semantically correct;
* queues and their DLQs have clear separation;
* parallel consumers use aligned rows or columns;
* labels are concise, legible at normal fit-to-screen zoom, and written in the user's language;
* service labels pair the official AWS name with a short human description of its role;
* edge labels are an active verb and the object being moved or accessed;
* implementation terms appear only when they change the architecture or are the clearest name for the audience; otherwise use plain language and move exact operations to Markdown;
* opaque decision codes, long decoding legends, black text, and AI-style headings or status phrases do not appear when a direct phrase such as `Store as escape`, `Dead-letter property`, or `x validation` communicates the same fact;
* arrows do not cross labels, icons, or unrelated flows;
* two-way communication uses two directional arrows, not one ambiguous bidirectional arrow;
* use rounded orthogonal connections only for long routes with multiple bends, not as a global style;
* official AWS4 resource icons keep their service/category default fill and white stroke instead of receiving a global orange or semantic error color;
* use `78 x 78 px` and 12 pt labels as the AWS resource-icon baseline; vary size only for deliberate focal emphasis;
* do not mix AWS3 and AWS4 icon generations on the same page without an explicit legacy justification;
* a DLQ keeps the default Amazon SQS icon color; show failure semantics with a red dashed connector and concise label;
* nested boundaries must represent real hierarchy such as `cloud -> account -> application -> bounded context`, with inner boundaries visually lighter than trust boundaries;
* horizontal Lambda wrappers are appropriate for dense aligned groups of functions, not isolated focal Lambdas;
* whitespace and alignment provide grouping instead of decorative boxes.

Connection notation is a team convention, not an AWS mandate. When the drawing uses it, include a compact legend:
* solid: synchronous call;
* dashed and optionally animated: asynchronous flow;
* red dashed: retry, failure, or DLQ path.

Do not claim that animated arrows are an official AWS architecture requirement.

### 7. Review visible text for human readability
Read every title, component label, edge label, legend, and decision note as prose written for the intended audience.
* If a humanizer skill is available, invoke it for visible prose while preserving technical facts, AWS service names, resource identifiers, and interaction semantics.
* If no humanizer skill is available, perform the same review manually.
* Remove AI-draft residue: coded decision badges, staged or inflated headings, all-caps status text, decorative bold, repetitive labels, formulaic phrasing, and long legend prose.
* Prefer a direct description of behavior over raw implementation vocabulary when both are accurate. For example, use `Stores raw data` as an events label instead of `TransactionId -> resource + bucket`. Use `Queries DB` unless the team's established notation mandates `DynamoDB GetItem`.
* Keep one compact notation legend and, when needed, one concise unresolved-decision note per page. Move the complete decision list to Markdown.
* Do not simplify away a fact that changes architecture semantics.

### 8. Use Mermaid for temporal behavior
Read `references/mermaid-patterns.md` before producing behavioral diagrams.

Use:
* `sequenceDiagram` for ordered interactions and ownership;
* `alt` / `else` / `end` for mutually exclusive outcomes;
* `opt` / `end` for optional behavior;
* `loop` / `end` for bounded retries;
* `par` / `and` / `end` only for genuine concurrency;
* notes for assumptions that are not components.

Do not use retries for definitive failures such as a snapshot removed by TTL unless a recovery process has already been requested and the retry is waiting for that process.

### 9. Perform the AWS architecture review
Read `references/aws-architecture-checklist.md` and assess applicable items, especially:
* idempotency at ingestion and consumer boundaries;
* write-then-publish failure windows;
* queue and DLQ retentions;
* snapshot TTL versus end-to-end replay window;
* strongly versus eventually consistent reads;
* event ordering and late events;
* payload limits;
* external API rate limits and backoff;
* consumer isolation;
* data classification, encryption, and retention;
* observability and operational recovery.

Do not silently add components to fix a concern. Present material alternatives as choices that still need approval.

### 10. Validate and render
Use the bundled validator when applicable:
```python
python <skill-source>/scripts/validate_drawio.py <diagram.drawio-or-xml>
```
When draw.io CLI is available, export every relevant page:
```
drawio --export --format png --page-index <index> --output <temporary.png> <diagram>
drawio --export --format pdf --all-pages --output <temporary.pdf> <diagram>
```
For Mermaid, render every block with an available Mermaid CLI. Use a temporary installation only with user permission or when the environment policy allows it.

Visually inspect:
* fit-to-screen readability;
* clipped or tiny labels;
* excessive canvas whitespace;
* generic boxes around AWS resources;
* confusing queue/DLQ proximity;
* crossed, detached, or backwards arrows;
* labels placed over edges, component captions, or other labels;
* headings, decision markers, or legends that read like AI-draft residue instead of normal technical writing;
* raw SDK, IaC, or implementation terms that are unexplained or unnecessary on the main canvas;
* opaque acronyms or decision codes that force the reader to consult a separate key;
* flows that imply false sequencing;
* differences between Mermaid and draw.io semantics.

Iterate until the rendered artifact is understandable without verbal explanation.

## Architecture patterns

### Event-driven fan-out
```
Producer -> EventBridge -> rule per intent -> SQS per critical consumer -> Consumer
```
Each critical consumer owns retry, DLQ, redrive, and idempotency. Failure in one consumer must not block another.

### Claim-check or snapshot reference
```
Producer -> immutable snapshot store
Producer -> lightweight event containing snapshotKey
Consumer -> snapshot store using snapshotKey
```
Persist the snapshot before publishing the reference. The snapshot store is not automatically the system of record.

### TTL-expired recovery
The primary control is retention alignment: a snapshot must remain valid while any message can still be processed or redriven.

If centralized recovery is approved:
```
Consumer -> central recovery-request queue -> rehydrator -> external source -> snapshot store
```
The consumer must persist the recovery request before relinquishing or delaying ownership of the original message. Recovery requests and effects must be idempotent. Data fetched later is current state, not a guaranteed historical reconstruction, and must be marked accordingly.

## Anti-patterns

Reject or explicitly flag:
* full business documents placed on an event bus without size and governance validation;
* a reference event whose target expires before queue and DLQ recovery windows;
* blind retry of a definitive TTL expiration;
* consumers implementing direct fallback to the external system independently;
* one mutable `DynamoDB` record used to process historical events;
* DLQs without ownership, alarms, and redrive procedure;
* datastore-to-event-bus arrows without an actual publishing mechanism;
* global ordering claims for EventBridge or standard SQS;
* automatic rehydration presented as historical reconstruction;
* long narrative text scattered around the infrastructure drawing;
* coded decision badges such as `B1` (though `D6` paired with a long decoding legend);
* raw labels such as `TransactionId, event.source mapping, or validator` when a direct description is equally accurate and easier for the audience to read;
* `black box` as a default label for systems that can be described as `Store as escape` or by their real role;
* generic shapes where official AWS icons exist;
* multiple scenarios compressed into one unreadable canvas.

## Completion standard

Report:
* files changed;
* pages or Mermaid diagrams added or removed;
* important architectural choices represented;
* decisions still requiring validation;
* structural validators executed;
* renderers used and pages visually inspected;
* whether visible labels received the human-readability pass and any technical terms intentionally retained;
* any limitation that could not be verified.

Never claim visual quality without rendering when a renderer is available.
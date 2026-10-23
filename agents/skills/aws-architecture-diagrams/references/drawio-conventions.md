# draw.io Conventions for AWS Architecture

## Preserve before changing

* Re-read the file immediately before every edit batch.
* Detect user edits made in the draw.io application and preserve them.
* Record page names, IDs, parent relationships, geometry, styles, labels, source/target IDs, and AWS shape identifiers.
* Prefer modifying existing cells and styles to introducing replacements.
* Do not convert a working uncompressed file to compressed content merely for formatting.
* Do not flatten editable components into images.

## Official AWS components

Prefer existing styles from neighboring cells. Common draw.io AWS shape attributes include:

```
shape=mxgraph.aws4.resourceIcon
resIcon=mxgraph.aws4.lambda
resIcon=mxgraph.aws4.sqs
resIcon=mxgraph.aws4.eventbridge
resIcon=mxgraph.aws4.dynamodb
resIcon=mxgraph.aws4.api_gateway
shape=mxgraph.aws4.group
grIcon=mxgraph.aws4.group_aws_cloud
grIcon=mxgraph.aws4.group_account
```

Do not guess an icon identifier without checking that the installed draw.io build renders it.

The service/category color is part of the official AWS4 icon style. When a trusted reference drawing is available, extract and reuse the exact style instead of applying one color to every resource. Common AWS4 defaults include:

```
Lambda       fillColor=#F78E04; strokeColor=#FFFFFF
Amazon S3    fillColor=#4F7D3D; strokeColor=#FFFFFF
Amazon SQS   fillColor=#D05C90; strokeColor=#FFFFFF
EventBridge  fillColor=#D05C90; strokeColor=#FFFFFF
DynamoDB     fillColor=#36469C; strokeColor=#FFFFFF
CloudWatch   fillColor=#D05C90; strokeColor=#FFFFFF
```

Never apply a global `fillColor=#F78E04` to all AWS resources. Do not recolor an Amazon SQS icon red merely because it is a DLQ; preserve the SQS default and communicate the failure role through the red dashed edge, the `DLQ` label, and spatial separation.

Use `78 x 78 px` geometry and `fontSize=12` as the baseline for standalone AWS4 resource icons. A focal component may be larger when the hierarchy is deliberate, but neighboring peers should remain aligned and consistently sized.

Use one AWS icon generation per page and prefer AWS4 for new work. Do not mix `mxgraph.aws3.*` and `mxgraph.aws4.*` to obtain a preferred color or illustration. A legacy exception must be explicit and visually reviewed.

External systems may use an existing neutral illustration style already present in the source drawing. Do not label an AWS service icon as an external product.

## Layout

* Main flow reads left to right.
* Use one primary flow per horizontal lane. Put a secondary query or command path on a separate row with a short, plain-language heading.
* Keep the ingress, orchestration, routing, consumer, and storage areas visually distinct through alignment and whitespace.
* Use whitespace before adding decorative boundaries or explanatory prose.
* Do not keep an optional or unresolved connection by routing it around the perimeter of the drawing. Move the choice to a short note or the supporting Markdown until the flow is approved.
* Align parallel consumers to a shared grid.
* Keep at least one icon-width of space between a queue and its DLQ; use more when labels or branch lines occupy the gap.
* Position DLQs consistently relative to their source queues.
* Put shared stores where consumer read lines can reach them without crossing the primary event path.
* Keep external APIs outside AWS boundaries.
* Use nested boundaries only for real hierarchy, for example `AWS Cloud -> account -> application -> bounded context`.
* Keep cloud and account trust boundaries visually dominant; application and bounded context boundaries should be lighter or dashed.
* Do not add a bounded-context-box merely to decorate a cluster whose ownership or semantics are unchanged.
* Avoid excessive canvas dimensions that make labels unreadable at fit-to-screen zoom.

## Labels and prose

Write for the people reviewing the architecture. The canvas is not a copy of the code, Terraform, SDK calls, or a draft produced by an AI assistant.

* Use the user's language for editorial text.
* Keep official AWS service names and exact resource identifiers. Put a resource identifier on a secondary line only when it helps the review.
* Pair the service name with a short description of its role, such as `Amazon SQS` and `Fila de entrada`.
* Write edge labels as an active verb plus the object, such as `Armazena a mensagem`, `Consulta pedidos`, or `Publica o evento`.
* Prefer plain behavior over implementation vocabulary when both remain accurate. Examples:
  * `Grava os dados` or `evento: pedido inserido` instead of `TransactionId -> resource + bucket`.
  * `Entrega a mensagem` instead of `event source mapping`.
  * `Eventos a publicar` instead of `outbox` when the data pattern does not need to be named on the canvas.
  * `Store as escape` or the actual system role instead of `black box`.
* Keep a technical term when it names a mechanism the architecture review depends on, such as `DynamoDB Streams`, `DLQ`, `PutEvents`, or an exact endpoint. Explain an acronym in the compact memory legend when the audience may not know it.
* Do not use opaque decision badges such as `B1`, `D6`, or `Decision point`. State the unresolved choice directly in a short local note or one concise note for the page.
* Avoid all-caps status text, staged headings such as `PROPOSAL FOR VALIDATION`, decorative bold on every line, inflated claims, repeated labels, and long prose legends.
* Attach only short technical details to the relevant component or edge.
* Do not place responsibility paragraphs, full JSON, or complete decision lists on the infrastructure canvas.
* Use unbiased text for the title, lane headings, one compact legend, and concise proposal or decision notes.
* Move contracts, detailed data models, operating procedures, and the complete decision list to Markdown.
* If a humanizer skill is available, invoke it for visible prose without changing technical facts or identifiers. Otherwise apply this checklist manually.

## Connections

Use directional arrows and orthogonal routing. Connectors are 1 pt and `#545B64` by default, with `endArrow=block`; omit `strokeWidth` or set `strokeWidth=1`. Do not use 2 pt as the global default. Reserve thicker connectors for an explicitly approved emphasis that remains consistent in the legend.

Use `rounded=0` for short direct routes. Use `rounded=1` only when a long orthogonal route has multiple bends and rounding materially improves traceability. Do not round all edges globally.

Team convention when explicitly adopted:

```
solid gray                 = synchronous request or durable write/read
dashed gray + flowAnimation = asynchronous delivery
dashed red + flowAnimation  = retry, failure, DLQ, or redrive
```

This notation is not an official AWS standard. Include a legend and apply it consistently.

Rules:

* Two calls in opposite directions require two arrows.
* A response arrow should not imply a second initiating request.
* A datastore does not forward an event unless an explicit stream/publisher is drawn.
* Persist-then-publish should be two numbered arrows from the producer.
* Do not draw EventBridge as guaranteeing global ordering.
* Keep DLQ paths visually secondary to the happy path.

## Lambda representation

Use the existing official Lambda resource icon. A standalone focal Lambda should remain an icon with a concise label. For a dense aligned group of two or more related functions, a compact horizontal wrapper may improve scanning by placing the Lambda icon at the left and the function name or operation at the right.

If a user-object wrapper provides a right-side label:

* preserve the wrapper unless it causes visible generic borders;
* keep wrapper dimensions and icon positions consistent across the group;
* remove decorative borders while keeping the AWS icon;
* anchor edges so they do not run through the Lambda name;
* keep the name readable without creating a generic-box visual.
* Do not wrap an isolated Lambda merely for visual decoration.

## Pages

Default structure:
1. Infrastructure principal in draw.io.
2. Behavioral scenarios in Mermaid, not duplicated into draw.io.

Add additional draw.io pages only when the user explicitly needs separate infrastructure views, accounts, regions, deployment stages, or trust boundaries.

## XML integrity

Validate:
* XML parsing;
* unique IDs within each diagram;
* valid `parent`, `source`, and `target` references;
* page count and names;
* expected AWS shapes;
* one AWS icon generation per page unless a legacy exception is explicit;
* connector widths consistent with the 1 pt default;
* no global orange override on AWS resource icons;
* no orphan child cells;
* no hidden or zero-size cells carrying encoded or unexpectedly long content;
* no accidental embedded-raster replacement of editable content.

Compressed draw.io pages must be decoded before cell-level validation. Use the bundled validator.

## Visual validation

Export every relevant page using draw.io CLI when available. Inspect the rendered image at normal width and fit-to-screen scale.

Reject the result if:
* important labels are tiny or clipped;
* components appear inside the wrong boundary;
* queue and DLQ relationships are ambiguous;
* edge labels overlap component captions, other labels, or icons;
* lines cross unrelated components;
* a branch appears disconnected;
* a secondary flow is not visually separated from the primary flow;
* visible text contains opaque decision codes, unexplained implementation jargon, AI-style status language, or a long decoding legend;
* the drawing uses `black box` where a real role or `Store as escape` would be clearer;
* the drawing requires a verbal walkthrough to identify the main flow;
* static export and interactive draw.io rendering differ materially.
# Mermaid Patterns for AWS Architecture

Use Mermaid for behavior and timing. Keep infrastructure topology in draw.io unless the user requests a Mermaid infrastructure view.

## Happy path

```mermaid
sequenceDiagram
    External source->>API Gateway: Submit event
    API Gateway-->>External source: Acknowledge
    API Gateway->>Input SQS: Route event
    Input SQS->>Lambda worker: Poll for message
    Lambda worker->>Snapshot store: Persist immutable snapshot
    Snapshot store-->>Lambda worker: Success
    Lambda worker->>EventBridge: Publish lightweight reference
    EventBridge->>Consumer SQS: Route matching event
    Consumer SQS->>Consumer app: Read event/reference
    Consumer app->>Snapshot store: Fetch snapshot
    Snapshot store-->>Consumer app: Snapshot payload
```

## Conditional outcomes

`alt` is equivalent to `if / else` and does not represent a component.

```mermaid
sequenceDiagram
    alt Condition A
        A->>B: First outcome
    else Condition B
        A->>C: Alternative outcome
    end
```

Use `opt` when there is only one optional path:

```mermaid
sequenceDiagram
    opt Optional notification
        A->>B: Notify
    end
```

## Bounded retry

```mermaid
sequenceDiagram
    SQS->>Consumer: Deliver message
    Consumer->>External API: Request
    External API-->>Consumer: Retryable failure
    Consumer-->>SQS: No acknowledgement
    loop Until maxReceiveCount
        SQS->>Consumer: Redeliver
        Consumer->>External API: Retry with backoff
    end
    SQS->>DLQ: Move after retry limit
```

Never use this pattern for a definitive condition that cannot change without a separate recovery action.

## Snapshot expired by TTL with centralized recovery

```mermaid
sequenceDiagram
    Consumer SQS->>Consumer: Deliver original event
    Consumer->>Snapshot store: Fetch snapshot
    Snapshot store-->>Consumer: Not found
    Consumer->>Recovery request SQS: Put recovery request
    Recovery request SQS-->>Consumer: Accepted
    Consumer-->>Consumer SQS: Leave original message unacknowledged
    Rehydrator->>Recovery request SQS: Poll
    Recovery request SQS-->>Rehydrator: Deliver recovery request
    Rehydrator->>Authoritative source: Fetch current state
    Authoritative source-->>Rehydrator: Return current state
    Rehydrator->>Snapshot store: Persist recovered snapshot with orig snapshot key
    Consumer SQS->>Consumer: Redeliver original event
    Consumer->>Snapshot store: Fetch snapshot
    Snapshot store-->>Consumer: Recovered snapshot
    Consumer-->>Consumer SQS: Acknowledge
```

Include these qualifications:

* the recovery queue owns retry and a DLQ;
* duplicate recovery requests are idempotent;
* the original message is left unacknowledged only after the recovery request is durably accepted;
* visibility timeout and backoff allow recovery to complete;
* data fetched later is current state, not a historical reconstruction;
* consumers requiring historical state use controlled manual treatment;
* if recovery exceeds `maxReceiveCount`, redrive occurs only after recovery completes.

## Write succeeded, publication failed

```mermaid
sequenceDiagram
    Input SQS->>Hydrator: Deliver event
    Hydrator->>DynamoDB: Put immutable snapshot
    DynamoDB-->>Hydrator: Success
    Hydrator->>EventBridge: Publish
    EventBridge-->>Hydrator: Publication fails
    Hydrator-->>Input SQS: Do not acknowledge
    Note right of Input SQS: Retry
    Input SQS->>Hydrator: Deliver event
    Hydrator->>DynamoDB: Check eventId and publication state
    DynamoDB-->>Hydrator: Snapshot already exists
    Note right of Hydrator: Retry publication only
    Hydrator->>EventBridge: Publish
    EventBridge-->>Hydrator: Accepted
    Hydrator-->>Input SQS: Success
```

Mark outbox or streams as a decision unless already approved.

## Consumer isolation

```mermaid
sequenceDiagram
    par Independent SAP delivery
        EventBridge->>SAP SQS: Route matching event
        SAP SQS->>SAP consumer: Deliver
        SAP consumer-->>SAP SQS: Acknowledge
    and Independent MF4 delivery
        EventBridge->>MF4 SQS: Route matching event
        MF4 SQS->>MF4 consumer: Deliver
        MF4 consumer-->>MF4 SQS: Acknowledge
    end
```

Use `par` only when paths are genuinely independent.

## Diagram quality

* Use descriptive participant aliases.
* Keep messages concise and directional.
* Avoid semicolons in sequence message text because some Mermaid versions parse them as statement separators.
* Use notes for assumptions and warnings, not additional pseudo-components.
* Avoid excessive nested `alt` and `loop` blocks; split the scenario when necessary.
* Validate every block with the target Mermaid version.
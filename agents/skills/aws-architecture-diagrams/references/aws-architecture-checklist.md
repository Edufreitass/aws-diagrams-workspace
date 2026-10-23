# AWS Architecture Review Checklist

Use only sections relevant to the system. Treat unresolved items as decisions, not assumed requirements.

## Boundaries and ownership

* Identify the system of record for every business entity.
* Distinguish temporary snapshots, caches, projections, and operational views from authoritative data.
* Show AWS Cloud and account boundaries accurately.
* Identify external systems without representing them as AWS services.
* Assign operational ownership for queues, DLQs, alarms, redrive, and recovery.

## Communication semantics

* Verify the initiator and direction of every arrow.
* Distinguish synchronous API calls from asynchronous delivery.
* Show request and response separately when both matter.
* Verify that labels name the action or payload, not a vague relationship.
* Do not put a datastore inline as if it forwards messages unless an explicit stream or change-data mechanism exists.
* Avoid global ordering claims for EventBridge and standard SQS.

## Ingress

* Validate authentication, authorization, request validation, throttling, and abuse protection.
* Return to the external caller according to the real acknowledgement contract.
* Persist before acknowledgement when loss is unacceptable.
* Define duplicate event behavior and idempotency key.
* Define malformed and functional-error handling without infinite retry.

## Event publication

* Keep event envelopes stable and versioned.
* Prefer lightweight events with immutable references when documents are large or shared.
* Validate EventBridge and SQS payload limits.
* Define source, detail type, schema version, occurred time, correlation ID, and idempotency key when applicable.
* Verify rule ownership and filtering by stable fields.
* Ensure adding a consumer does not require changing the producer unless contract evolution requires it.

## Write-then-publish reliability

For a producer that persists and then publishes:

* Persist before publishing any reference.
* Handle write succeeded / publish failed explicitly.
* On retry, avoid repeating external calls and durable effects unnecessarily.
* Decide whether idempotent retry plus source-queue retry is sufficient.
* Evaluate outbox, DynamoDB Streams, or another atomic publication pattern only as an explicit architectural decision.

## SQS and DLQ

* Use a queue per critical consumer when isolation is required.
* Give each queue an appropriate DLQ.
* Configure visibility timeout relative to processing duration.
* Configure bounded retry and backoff intentionally.
* Keep DLQ retention and snapshot retention compatible with investigation and redrive.
* Alarm on queue age, depth, DLQ depth, and repeated failures.
* Define partial batch failure behavior for Lambda event source mappings.
* Make redrive idempotent and independently executable per consumer.
* Do not expect a DLQ to notify a recovery component unless an explicit trigger or operational process exists.

## Idempotency

* Deduplicate ingress using a stable producer event ID.
* Deduplicate each consumer using event ID plus consumer identity.
* Make recovery requests idempotent.
* Make external side effects idempotent and protect them with a durable completion record.
* Distinguish `processing`, `completed`, and `publication pending` when recovery depends on state.
* Define concurrency behavior for duplicate deliveries.

## DynamoDB snapshots

* Use an immutable key per event when consumers require event-time consistency.
* Avoid a single overwritten `current` item as the basis for historical event processing.
* Validate the 400 KB item limit using observed production-like payloads.
* Decide whether consumers need strongly consistent `GetItem` reads immediately after publication.
* Use conditional writes where duplicate creation is possible.
* Keep schema version and retrieval timestamp.
* Treat TTL as asynchronous physical deletion and validate `expired` logically.
* Never infer validity only from physical item existence.
* If a `latest` view is useful, keep it separate from immutable consumer references.

## TTL and replay

* Define:
  * `snapshot validity >= maximum end-to-end message age`
  * `= investigation/redrive window`
  * `+ operational margin`
* Consider:
  * ingress delay;
  * consumer queue retention;
  * processing retries;
  * consumer outage;
  * DLQ retention;
  * incident investigation;
  * redrive execution;
  * internal data-retention policy.
* If a snapshot can expire while its message remains recoverable, the architecture has a broken retention invariant.

## Recovery after snapshot expiration

* Do not blindly retry `GetItem` after definitive TTL expiration.
* Use a durable and explicit channel for centralized recovery requests when automated recovery is approved.
* Persist the recovery request before acknowledging or abandoning the original message.
* Configure retry and DLQ for the recovery channel.
* Deduplicate by original event ID and snapshot key.
* Rate-limit calls to the external source.
* Mark later-fetched data as recovered current state.
* Do not claim that current source data reconstructs an historical snapshot.
* Define which consumers may accept recovered current state.
* Send historically strict consumers to controlled manual treatment.
* Avoid unbounded loops among consumer, event bus, and hydrator.

## Ordering and late events

* Assume events for one entity may arrive out of order unless a concrete ordering mechanism exists.
* Carry occurred time and relevant previous/current state in the event envelope.
* Preserve each event's immutable snapshot.
* Define per-consumer late-event policy.
* If strict per-entity ordering is required, evaluate FIFO queues and grouping keys explicitly.
* Do not assume FIFO solves business-level version conflicts without consumer logic.

## External API integration

* Centralize credentials, mTLS, authentication, timeout, retry, and error mapping when multiple consumers need the same source.
* Validate rate limits and concurrency limits.
* Use bounded exponential backoff with jitter for retryable failures.
* Separate transient failures from functional errors and not-found results.
* Avoid consumer-specific fallback calls that produce inconsistent versions of shared data.

## Security and governance

* Classify order and customer data.
* Validate encryption in transit and at rest.
* Minimize IAM permissions between queues, Lambdas, EventBridge, and DynamoDB.
* Avoid secrets in diagrams, logs, events, and examples.
* Define retention and deletion policy.
* Validate whether snapshots may contain regulated or personal data.
* Define access for incident investigation and redrive.

## Observability

* Correlate event ID, order/entity ID, snapshot key, consumer ID, and request ID.
* Measure hydration latency, external API latency, publication failures, queue age, retry count, DLQ depth, snapshot misses, and recovery outcomes.
* Alert before oldest-message age approaches snapshot expiration.
* Record functional rejection reasons without treating them as successful hydration.
* Preserve enough metadata to audit redrive and recovery.

## Diagram review

* Main flow is understandable left to right.
* Every component uses correct official iconography.
* Names are legible at fit-to-screen zoom.
* Queues and DLQs are visually distinct and sufficiently separated.
* No arrow crosses an icon, label, or unrelated flow.
* Asynchronous notation has a legend if nonstandard styling is used.
* Proposed components and unresolved choices are visibly marked.
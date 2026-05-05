# RECNO parity roadmap (3x-ui / Marzban)

This document breaks “full feature parity” into concrete implementation stages so work can be delivered safely and verified incrementally.

## Stage 1 — Stability baseline (must-have)

- [ ] End-to-end subscription correctness for all protocols (vless/vmess/trojan/hysteria2), including import in common clients.
- [ ] Unified inbound validation rules by protocol (server-side schema + client-side dynamic form logic).
- [ ] Deterministic key lifecycle (create/rotate/revoke) and migration for existing users without keys.
- [ ] Error observability: structured API errors + UI surfacing + server-side logging around config generation and restart.
- [ ] UI consistency pass: language/theme consistency across all components and dialogs.

## Stage 2 — Transport/security completeness

- [ ] Reality full settings: `dest`, `serverNames`, `shortIds`, flow options, fingerprints matrix.
- [ ] WS/gRPC/XHTTP complete parameter set (path/serviceName/headers/authority modes).
- [ ] TLS controls: ALPN presets, SNI policies, cert strategy, per-inbound options.
- [ ] Per-protocol capability matrix shown in UI (enable/disable invalid combinations).

## Stage 3 — Subscription and output ecosystem

- [ ] Multiple subscription render modes (raw/base64/json profile adapters).
- [ ] Client-specific formatting strategies and compatibility switches.
- [ ] Profile metadata controls (title/interval/web page) and strict header conformance.
- [ ] User-level include/exclude rules (inbound filtering in generated subscriptions).

## Stage 4 — Operations and security

- [ ] Access control model (roles, scoped permissions, audit log).
- [ ] Node orchestration reliability (sync status, retries, drift detection).
- [ ] Guardrails: brute-force protection, API rate limits, optional fail2ban integration.
- [ ] Metrics dashboard: service health, inbound/user traffic trends, alert rules.

## Stage 5 — UX polish

- [ ] Complete i18n coverage (RU/EN), including toasts/validation/errors.
- [ ] Motion system with performance budget for low-end phones.
- [ ] Interaction parity with mature panels for modal flows and onboarding steps.

## Delivery policy

1. Every stage ships with migration notes and rollback path.
2. No protocol feature is marked complete without real client import tests.
3. UI-only changes are not accepted unless matching backend validation exists.

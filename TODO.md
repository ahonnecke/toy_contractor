# TODO: Next Iteration Improvements

## 0. Database and API
- [x] switch from sqlite to redis
- [ ] Add revision tracking to the schema
- [ ] change list contracts to only list the most recent version of a contract, ignore the past revisions
- [ ] add list revisions to api (takes a contract id)
- [ ] add the inputted language to the db (so for a revision we record the NLP intput

## 1. Multi-Tenancy with JWT + Quotas (Redis)
- [ ] Add **Auth0 / simple JWT auth** in FastAPI (use `fastapi-jwt-auth`).
- [ ] Define `tenant_id` claim in JWT; attach it to every request via FastAPI dependency.
- [ ] Update DB schema (contracts/versions) to include `tenant_id` column.
- [ ] Add query filters so each tenant can only see their own contracts.
- [ ] Introduce **per-tenant rate limiting / quotas**:
  - [ ] Use Redis to store request counts per `tenant_id`.
  - [ ] Enforce a limit (e.g. 100 requests/hour).
  - [ ] Return HTTP 429 when exceeded.
- [ ] Add integration test: one tenant cannot access another’s contracts.

## 2. Prometheus Metrics
- [ ] Add **prometheus-client** dependency.
- [ ] Expose `/metrics` endpoint in FastAPI (Scrapeable by Prometheus).
- [ ] Instrument:
  - [ ] API request count / latency (per endpoint).
  - [ ] LLM call latency and token usage.
  - [ ] Cache hit/miss for Redis.
- [ ] Add Prometheus service to `docker-compose.yml`.
- [ ] Add Grafana service to `docker-compose.yml` with a starter dashboard (LLM latency, contract drafts per tenant, etc.).
- [ ] Write doc snippet: “How to view metrics in Grafana.”

## 3. RAG Knowledge Base (Redis Vector)
- [ ] Add Redis module for vectors (`redis-py` with `RediSearch` / `redisvl`).
- [ ] Add service to `docker-compose.yml` with vector indexing enabled.
- [ ] Create embeddings for stored contracts/clauses:
  - [ ] Use a sentence-transformer (e.g. `all-MiniLM-L6-v2`) or Mistral’s embedding endpoint (if available).
  - [ ] Store embeddings in Redis with metadata (`tenant_id`, contract_id, clause_id).
- [ ] Implement `/contracts/search` endpoint:
  - [ ] Given a query, embed and retrieve top-N relevant clauses/contracts from Redis.
  - [ ] Include retrieved snippets in the prompt context when drafting/refining.
- [ ] Add integration test: searching for "termination" returns contracts with termination clauses.
- [ ] Document RAG workflow in README.

---

## Stretch Goals
- [ ] Cache LLM outputs (Redis key = hash of prompt).
- [ ] Add tracing (OpenTelemetry) for FastAPI + Redis + Mistral calls.
- [ ] Dashboard: show which tenants use the most tokens and top search queries.

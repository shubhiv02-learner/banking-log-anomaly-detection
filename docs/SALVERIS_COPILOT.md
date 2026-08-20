# Salveris Copilot integration

SentryyIQ never exposes Salveris to the browser. The Copilot UI calls SentryyIQ only.

## Env (server)

| Variable | Role |
|----------|------|
| `SALVERIS_BASE_URL` | Salveris origin (not SentryyIQ port — e.g. `http://localhost:8001` if API is `:8000`) |
| `SALVERIS_CALLING_PLATFORM_ID` | SentryyIQ platform UUID |
| `SALVERIS_SERVICE_PRINCIPAL_ID` | Calling **service** principal |
| `SALVERIS_CLIENT_SECRET` | Service secret |
| `SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID` | Alice's Salveris acting principal (seed script) |
| `SALVERIS_BOB_ACTING_PRINCIPAL_ID` | Bob's Salveris acting principal (seed script) |
| `JWT_SECRET` | Signs SentryyIQ login tokens |

Copy from [`.env.example`](../.env.example) into your local `.env`.

There is no signup. Seed Alice and Bob (mapped to those Salveris IDs):

```text
python -m backend.scripts.set_user_credentials --seed-alice-bob
```

Local-dev defaults: `alice@sentineliq.demo` / `Alice123!` and `bob@sentineliq.demo` / `Bob123!`.

## Flow

1. UI signs in (`POST /auth/login`) then calls `POST /copilot/ask` or `POST /copilot/search` with `Authorization: Bearer <jwt>`
2. `CopilotService` → `resolve_acting_principal(user)` from `user_master.external_reference`
3. `SalverisClient.search/answer(..., acting_principal_id=...)`

Salveris inbound contract:

- `POST {SALVERIS_BASE_URL}/v1/knowledge/search`
- `POST {SALVERIS_BASE_URL}/v1/knowledge/answer`
- Headers: `Authorization: Bearer {SALVERIS_CLIENT_SECRET}`, `X-Salveris-Calling-Platform-Id`, `X-Salveris-Service-Principal-Id`, `X-Salveris-Acting-Principal-Id`
- Body: `{ "query": "<text>" }` only (extra fields are rejected with 400 `Invalid request.`)

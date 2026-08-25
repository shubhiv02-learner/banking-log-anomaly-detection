# Salveris Copilot integration

SentryyIQ never exposes Salveris to the browser. The Copilot UI calls SentryyIQ only.

## Env (server)

| Variable | Role |
|----------|------|
| `SALVERIS_BASE_URL` | Salveris origin (not SentryyIQ port — e.g. `http://localhost:8001` if API is `:8000`) |
| `SALVERIS_CALLING_PLATFORM_ID` | SentryyIQ platform UUID |
| `SALVERIS_SERVICE_PRINCIPAL_ID` | Calling **service** principal |
| `SALVERIS_CLIENT_SECRET` | Service secret |
| `JWT_SECRET` | Signs SentryyIQ login tokens |

Acting principals are **not** application env. After seed they live on
`user_master.external_reference`. Copilot sends that value as
`X-Salveris-Acting-Principal-Id`.

There is no signup. Insert Alice, Bob, Rita, and Karan Malhotra only when
missing; fill empty password hash and Salveris principal:

```text
python -m backend.scripts.set_user_credentials --seed-alice-bob
```

Existing `user_master` emails are left unchanged. Karan Malhotra is matched
by name so an existing ops row keeps its notification mailbox. Bootstrap
principals: Alice `…031`, Bob `…032`, Rita `…034`, Karan `…03f`.

## Flow

1. UI signs in (`POST /auth/login`) then calls `POST /copilot/ask` or `POST /copilot/search` with `Authorization: Bearer <jwt>`
2. `CopilotService` → `resolve_acting_principal(user)` from `user_master.external_reference`
3. `SalverisClient.search/answer(..., acting_principal_id=...)`

`user_master.email` is the address sent on incident assign notifications
(`notify_n8n` payload `email`). Seed must not replace a real mailbox with a
demo address.

Salveris inbound contract:

- `POST {SALVERIS_BASE_URL}/v1/knowledge/search`
- `POST {SALVERIS_BASE_URL}/v1/knowledge/answer`
- Headers: `Authorization: Bearer {SALVERIS_CLIENT_SECRET}`, `X-Salveris-Calling-Platform-Id`, `X-Salveris-Service-Principal-Id`, `X-Salveris-Acting-Principal-Id`
- Optional Copilot domain overlay: `X-Salveris-Caller-Profile: sentryyiq`
- Body: `{ "query": "<text>" }` only (extra fields are rejected with 400 `Invalid request.`)

Live telemetry hops Salveris may call on this API (not on Salveris itself):
see [`COPILOT_TELEMETRY_PHASED_FETCH.md`](COPILOT_TELEMETRY_PHASED_FETCH.md).

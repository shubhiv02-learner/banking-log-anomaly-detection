# Salveris Copilot integration

SentryyIQ never exposes Salveris to the browser. The Copilot UI calls SentryyIQ only.

## Env (server)

| Variable | Role |
|----------|------|
| `SALVERIS_BASE_URL` | Salveris origin (not SentryyIQ port — e.g. `http://localhost:8001` if API is `:8000`) |
| `SALVERIS_CALLING_PLATFORM_ID` | SentryyIQ platform UUID |
| `SALVERIS_SERVICE_PRINCIPAL_ID` | Calling **service** principal |
| `SALVERIS_CLIENT_SECRET` | Service secret |
| `SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID` | Temporary **acting** principal (Alice) |

Copy from [`.env.example`](../.env.example) into your local `.env`.

## Flow

1. UI → `POST /copilot/ask` (Answer: grounded reply + sources) or `POST /copilot/search` (Search: passages only, no answer)
2. `CopilotService` → `resolve_acting_principal()` (config today)
3. `SalverisClient.search/answer(..., acting_principal_id=...)`

Salveris inbound contract:

- `POST {SALVERIS_BASE_URL}/v1/knowledge/search`
- `POST {SALVERIS_BASE_URL}/v1/knowledge/answer`
- Headers: `Authorization: Bearer {SALVERIS_CLIENT_SECRET}`, `X-Salveris-Calling-Platform-Id`, `X-Salveris-Service-Principal-Id`, `X-Salveris-Acting-Principal-Id`
- Body: `{ "query": "<text>" }` only (extra fields are rejected with 400 `Invalid request.`)

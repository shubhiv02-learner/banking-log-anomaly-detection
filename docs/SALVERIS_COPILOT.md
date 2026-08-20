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

1. UI → `POST /copilot/search` or `POST /copilot/ask`
2. `CopilotService` → `resolve_acting_principal()` (config today)
3. `SalverisClient.search/answer(..., acting_principal_id=...)`

Header names sent to Salveris (provisional): `X-Calling-Platform-Id`, `X-Service-Principal-Id`, `X-Client-Secret`, `X-Acting-Principal-Id`.

# Security audit: startup, credentials, and AI provider boundary

## Fixed

- Removed live OpenAI and Telegram credentials from deployment and documentation files.
- Replaced the corrupted ChatGPT service module with a bounded implementation.
- Repaired blueprint registration and removed imports of a missing database helper.
- Added validated secrets, non-wildcard CORS, production HTTPS-origin enforcement, request-size limits, and disabled-by-default registration.
- Prevented public self-registration as an administrator.
- Added provider timeouts, bounded retries, prompt-size limits, output validation, allow-listed assignment names, and deterministic fallbacks.
- Added security headers and production 5xx detail redaction.
- Added CI tests and tracked-file secret scanning.

## Required operator action

The previously committed OpenAI key, Telegram token, and JWT secret must be considered compromised. Rotate or revoke them in their respective services. Deleting values from the current branch is not sufficient because Git history and clones may retain them.

## Residual risks

- Existing route modules use broad exception handlers and some legacy SQLAlchemy query APIs. The application-level response filter prevents 5xx detail leakage, but route-level logging and narrower exception handling should be improved later.
- Login rate limiting and refresh-token revocation are not implemented.
- SQLite is acceptable for local use but unsuitable for durable multi-worker production storage.
- Database schema changes still rely on `create_all`; a migration tool should be introduced before production schema evolution.
- Telegram network calls remain synchronous and can add request latency, though their existing timeouts limit hangs.

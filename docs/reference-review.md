# Comparable backend review

## Dify (`langgenius/dify`)

Adopted idea: keep provider and application secrets outside source control, use sanitized environment templates, and make production configuration explicit.

Applied here: Render values are dashboard-managed, examples are empty, committed credentials are removed, and a secret regression check runs in CI.

## Langflow (`langflow-ai/langflow`)

Adopted idea: treat CORS as a security boundary and test wildcard behavior rather than relying on permissive framework defaults.

Applied here: origins are parsed centrally, wildcard origins are rejected, production requires HTTPS origins, credentialed CORS is disabled, and tests cover failure cases.

## Open WebUI (`open-webui/open-webui`)

Adopted idea: expose authentication and signup behavior as explicit deployment settings with restrictive defaults.

Applied here: public registration defaults off, public callers cannot choose the admin role, and a password-length floor is enforced before the legacy registration handler runs.

## Deliberately not copied

These projects include queues, migrations, distributed storage, and complex provider registries. Adding those systems to this small backend would increase operational risk without solving its immediate startup and credential problems.

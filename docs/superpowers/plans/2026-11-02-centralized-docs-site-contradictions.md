# Centralized docs site: contradictions found while merging

Where the heimdall-api documentation site and heimdall-docs stated the same fact differently, the code at the
pinned commits (heimdall-api `82f7d353`, v4.2.0; heimdall-ui `82219b7`, v1.10.0) decided which statement the merged
site keeps. The pull request body quotes this file.

## Task 3: Overview, Architecture and Installation

### Between the two sites

| # | heimdall-docs said | The API site said | The code says | Kept |
| --- | --- | --- | --- | --- |
| 1 | Installation: `HEIMDALL_AUTH_TOKEN_SECRET` is a required setting, and `HEIMDALL_AUTH_TOKEN_SECRET_PREVIOUS` an optional one used while rotating it. | Getting started: `HEIMDALL_AUTH_SIGNING_KEY` (an ES256 P-256 key) and `HEIMDALL_APPLICATION_TOKEN_AUDIENCE` are required; `HEIMDALL_AUTH_SIGNING_KEY_PREVIOUS` is the rotation setting. | `docker-compose.yml` requires `HEIMDALL_AUTH_SIGNING_KEY`; `Security/ApplicationTokenOptions.cs` throws when the application audience is unset or collides with a person audience; `Registration/TokenSecurityRegistrationExtensions.cs` lists both `HEIMDALL_AUTH_TOKEN_SECRET` variables as retired, never read, and only warned about. | The API site. |
| 2 | Installation, Docker Compose: the template leaves `HEIMDALL_AUTH_TOKEN_SECRET` empty, and Compose will not start until it is set. | Environments and deployment: the template leaves `HEIMDALL_AUTH_SIGNING_KEY` empty. | `docker/local.env.example` has `HEIMDALL_AUTH_SIGNING_KEY=` and no token secret; `docker-compose.yml` fails with `set HEIMDALL_AUTH_SIGNING_KEY in the env file`. | The API site. |
| 3 | Architecture, system context: in each VPS environment `fortuna-api` is given the same `HEIMDALL_AUTH_TOKEN_SECRET` value as that environment's Heimdall API. | Operations and environments: only Heimdall holds the signing key; consumers verify with the public keys at `/.well-known/jwks.json`; the secret is retired and fortuna-api 4.0.0 no longer reads it. | As item 1: the secret is never read; tokens are ES256 and the public keys are served at `/.well-known/jwks.json`. | The API site: the bullet now says Fortuna verifies against the published keys and holds no secret of Heimdall's. |
| 4 | Overview: an application is owned by one Scope Admin **or System Admin** who owns its scope. | Overview vocabulary: an application is owned by exactly one **Scope Admin** who owns that scope. | `Handlers/CreateApplicationCommandHandler.cs` accepts an owner whose role is `ScopeAdmin` or `SystemAdmin` and who owns the scope (FR-AP-03 says the same). The doc comment on `Entities/Application.cs` still names only `ScopeAdmin`. | heimdall-docs. |

### Within the API site

| # | One page said | Another page said | The code says | Kept |
| --- | --- | --- | --- | --- |
| 5 | Overview: `Person` has no `ScopeId`; a person has no scope column. Domain model: `SCOPE_USER` remains the relationship "and every read goes through it". | Domain model: `PERSON.scope_id` is a copy of a User's `SCOPE_USER` scope, kept so a unique index can enforce per-scope email uniqueness. | `Entities/Person.cs:195-201` has `long? ScopeId`, a copy of the membership's scope for a User and `null` for administrators; `SCOPE_USER` remains the relationship, but a read that only needs the scope may take the column directly, and `EmailVerificationService.cs:50`, `PasswordResetService.cs:56` and `PersonEmailAuthorization.cs:29` do. | The code. The overview says the relationship lives in the join tables, the person row carries a copy of a User's scope for the index, and scope-only reads may use it; the domain model's "every read goes through it" is corrected the same way. |
| 6 | Overview: authentication reads no database per request, so a token can outlive the account it names until it expires. | Architecture: `ActorLivenessFilter` refuses a token whose person or Google User is absent or logically deleted, at one indexed read per request. | `Security/ActorLivenessFilter.cs` exists and is registered globally. | The architecture page. The overview says validation reads no database, but the named identity is checked on every authenticated request. |

### Against the code (no second statement)

These were stale facts on pages this task merged or moved; the code corrected them.

| # | The page said | The code says | Now |
| --- | --- | --- | --- |
| 7 | The pinned EF Core CLI is `dotnet-ef` 10.0.12. | `.config/dotnet-tools.json`: 10.0.13. | 10.0.13. |
| 8 | Clone with `--recurse-submodules`, because the documentation site's theme is a git submodule. | No `.gitmodules` at `82f7d353`. | A plain `git clone`. |
| 9 | The `docker` job in the `tests.yml` workflow checks that the API image builds. | No `.github/workflows` at `82f7d353`; `yggdrasil.yml` runs the `docker` check, `ci/docker.sh`, on Jenkins. | The Jenkins `docker` check. |
| 10 | The latest releases are API v1.4.0 and UI v1.6.1. | heimdall-api `CHANGELOG.md`: 4.2.0; heimdall-ui `CHANGELOG.md`: 1.10.0. | v4.2.0 and v1.10.0. |
| 11 | Every line of the tracked `Environments/.env` template holds a `[[...]]` placeholder. | `HEIMDALL_AUTH_SIGNING_KEY=` is empty in the template. | "Most lines", with the signing key named as the exception. |
| 12 | Environments and deployment (API site, moved here): yggdrasil's Jenkins runs this repository's `Jenkinsfile`. | No `Jenkinsfile` at `82f7d353` (commit `a82525ff` removed it); `yggdrasil.yml` is the pipeline file Jenkins reads. | The sentence names and links `yggdrasil.yml`. |

Not a contradiction, only a difference in precision: the heimdall-api README says `HEIMDALL_APPLICATION_TOKEN_AUDIENCE`
must differ from `HEIMDALL_AUTH_TOKEN_AUDIENCE`; the API site adds the two audiences derived from it, and
`ApplicationTokenOptions.Parse` checks all three. The merged page keeps the API site's wording.

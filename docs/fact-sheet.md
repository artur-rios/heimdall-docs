# Heimdall — fact sheet

The cited facts this site is written from, compiled 2026-10-13 from
`heimdall-api` and `heimdall-ui`. When a page and its source disagree, the
source wins: fix the page, then this file.

Compiled 2026-10-13 from local checkouts (read-only) plus `gh` queries. Every fact carries a source.

**Source abbreviations**

- `API/` = `D:\Repositories\heimdall-api` (local branch `release/1.4.0`; its tree is identical to
  `develop`; remote `main` = merge commit `cefac91` "release: v1.4.0 (#173)", 2026-10-13).
- `UI/` = `D:\Repositories\heimdall-ui` (local branch `develop`, commit `30f5449`; remote `main` =
  `3cf473a` "release: v1.6.1 (#118)". `develop` is 1 commit ahead of `main`: "chore: adopt the artur
  rios attribution license (#120)", touching `LICENSE`, `README.md`, `api/heimdall.json`,
  `.wakatime-project`. Source: `gh api repos/artur-rios/heimdall-ui/compare/main...develop`).
- `API-site:` = a page of `API/docs/content/en/docs/…` (published at https://docs.artur-rios.tech/heimdall-api/).
- `API-req:` = `API/docs/requirements/<file>`; `UI-req:` = `UI/docs/requirements/<file>`.

---

## 1. Pitch, what it is, what it is not

**Pitch (assembled only from sourced phrases).** Heimdall is a centralized identity-management
system for many client systems at once. It answers one question for every system that delegates to
it — *who is this caller, and what are they allowed to do?* — while keeping each client system's
identities isolated inside its own **scope** (API-site `_index.md` home lead; `docs/_index.md`). It
consists of the **Heimdall API**, "a centralized identity management API built with ASP.NET Core
(.NET 10)" (API/README.md intro; `gh repo view` description), and **Heimdall UI**, "the Flutter
front-end for the Heimdall API", one codebase shipping to Web, Windows, Linux and Android
(UI/README.md, Overview).

**What it is**

- Person management, application (non-human identity) management, authentication and authorization,
  password recovery, email verification and Google Sign-In, via scope-based multi-tenancy
  (API/README.md intro).
- Scope-specific permissions optionally folded into the JWT (`IncludeAsJwtClaim`) (API/README.md,
  Overview).
- Optional 2FA (authenticator app and/or email + single-use recovery codes) (API/README.md, Overview).
- Logical (soft) and hard deletion with defined cascades (API/README.md, Overview).
- LGPD/GDPR data-subject rights: export, erasure, restriction (API/CHANGELOG.md 1.0.0 "Added").
- Self-registration into scopes that open it (UC-47, API 1.4.0) and per-scope email links
  (FR-SR-10) (API/CHANGELOG.md 1.4.0).
- An interface where "what each person sees follows their role"; "a usability decision, not a
  security one: the API remains the sole authority" (UI/README.md, Overview).

**What it is not / exclusions (only those stated)**

- UI: "iOS and macOS are out of scope" (UI-req Vision Document §1.2); "No iOS or macOS platform
  folder exists" (UI-req Technology Stack Document §2).
- UI enforces no authorization: "hiding a control is a usability decision, never a security control"
  (UI-req System Requirements Document §5 NFR-08; Vision §7).
- UI holds no identity data, "caches nothing that outlives a session" (UI-req Vision §7).
- UI desktop/Android: "Signing and packaging (MSIX, AppImage, deb) are deployment decisions and are
  not part of this repository"; "No target auto-updates" (UI-req Operations & Infrastructure §6).
- API: no token revocation list — tokens are stateless signed JWTs; Google sign-out "revokes
  nothing" (API/README.md, Google Sign-In; API-site operations.md "Scaling").
- API rate limiter is "not a replacement for a WAF or an API gateway" (API-site operations.md,
  "Rate limiting and lockout" alert).
- API never migrates on start-up from source; it refuses to start with pending migrations (the Docker
  entrypoint applies them) (API/README.md, Migrations; "What the container does at start-up").
- PostgreSQL is deliberately not a service in the Compose file (API/README.md, Deploy with Docker).
- Google sign-in never creates/authenticates a Scope Admin or System Admin (FR-GO-04) (API/README.md,
  Google Sign-In).
- 2FA is not available to Google Users (API-site overview.md vocabulary; two-factor.md intro).
- The UI's metrics: "It exposes no metrics" (UI/CONTRIBUTING.md, Where this is deployed from).

---

## 2. Domain concepts

Source unless noted: API-site overview.md "The vocabulary"; API-req Vision Document §1.3, §8, §9;
API-req System Requirements Document §1.3.

| Concept | Definition |
| --- | --- |
| **Scope** | Logical tenant boundary grouping the owners, users, applications, Google Users and permissions of one client system. Has `GoogleSignInEnabled` (off by default) and, since 1.4.0, `SelfRegistrationEnabled` (default false, FR-SR-01) and optional `EmailVerificationUrl`/`PasswordResetUrl` (FR-SR-10) (API-req SRD §3.8a). |
| **Person** | Human identity: name, email, password hash, role, deletion status. "Has **no scope column**; its relationship to scopes is derived from its role." (but see §10 — `PERSON.scope_id` copy exists) |
| **Role** | Closed set of three rows: `SystemAdmin`, `ScopeAdmin`, `User`, in a `Role` table referenced by `RoleId`. |
| **SystemAdmin** | Belongs to no scope; governs the whole system. Since API 1.2.0 a System Admin **may own a scope** (FR-SC-08) and its applications (FR-AP-03) (API/CHANGELOG.md 1.2.0). |
| **ScopeAdmin / Scope Owner** | Owns 1..n scopes via `SCOPE_OWNER` (many-to-many). A ScopeAdmin with no live owned scope cannot authenticate (FR-AU-07, API-site domain-model.md "Deletion cascades"). |
| **User / Scope User** | Belongs to exactly one scope via `SCOPE_USER` (`SCOPE_USER.PersonId` unique). Same email may exist as a User in several scopes; admins' emails are unique system-wide (API-site flows/login.md "Which lookup"). |
| **Application** | Non-human identity in exactly one scope, owned by exactly one `ScopeAdmin` or `SystemAdmin` who owns that scope; "a `User` may never own one" (FR-AP-03) (API-site api-reference.md, Applications). |
| **Google User** | Authenticated by Google; always `User`-equivalent; exactly one scope; own `GOOGLE_USER` table with direct `ScopeId`; email unique within scope jointly with password Users (API-req Vision §9). |
| **Scope Permission** | Named permission inside a scope (`Name`, optional `Description`, `IncludeAsJwtClaim`). No owner — owning the scope is the whole authorization. A leaf (nothing references it). Flagged names are folded into the `scopePermissions` claim **at token issuance** (snapshot; picked up on next login). User → their scope's permissions; ScopeAdmin → union over owned scopes; SystemAdmin → none (API-site flows/scope-permission-claims.md). |
| **Two-Factor Auth** | Opt-in per person (all three roles), methods: authenticator app (TOTP, RFC 6238), email (6-digit code, 10 min), or both; ten single-use recovery codes. Lifecycle None → Pending (UC-36) → Active (UC-37) → None (UC-39); UC-40 regenerates codes (API-site flows/two-factor.md). TOTP secret encrypted at rest (ASP.NET Core Data Protection); recovery codes hashed; email codes hash + per-code salt (NFR-16). |
| **Challenge token** | Short-lived token with `mfaPending` claim returned by login when 2FA is active; accepted only at `POST /api/auth/2fa/verify` (and read from body by `2fa/challenge/resend`); single redemption (FR-2F-10); 5 guesses (FR-2F-17); lifetime **10 minutes** (NFR-17, API-req SRD §6). |
| **Internal Id / PublicId** | `Id` bigint never leaves the DB; `PublicId` GUID is used in paths, bodies, token claims (NFR-15) (API-site overview.md "Two identifiers per entity"). |
| **Logical deletion** | `IsDeleted = true`, row stays. Scope logical delete cascades to its Users, Google Users, applications — not owners, not permissions. Persons/Google Users/Applications/Permissions: own flag only. Never touches 2FA state. (API-site domain-model.md "Deletion cascades") |
| **Hard deletion** | Row removed. Scope → removes join rows, Users, Google Users, applications, permissions (FK `ON DELETE CASCADE` for permissions). ScopeAdmin → SCOPE_OWNER rows, owned applications, 2FA + recovery codes. User → SCOPE_USER row, 2FA. Google User/Application/Permission → leaf. Rejected if a scope would be left ownerless (NFR-12). Hard deletes are System-Admin-only. (same) |
| **Anonymisation** | Logically deleted identities are anonymised in place after 30 days (subject request, UC-42) or 90 days (admin deletion) (NFR-20) (API-site operations.md "Data retention — NFR-19"). |
| **Restriction of processing** | NFR-24: subject-requested suspension; restricted identity can still sign in but receives a **subject-rights-only token** (`subjectRightsOnly` claim, no scope; `processingRestricted: true` in the answer) accepted only by data-export, erasure-request, processing-restriction, processing-restriction/lift (API/CHANGELOG.md 1.3.0; API-site architecture.md). |
| **Two kinds of caller** | Password identities (`Person`, Argon2id hash + per-person salt, `POST /api/auth/login`, roles User/ScopeAdmin/SystemAdmin, optional 2FA) vs Google identities (`GoogleUser`, no hash, `POST /api/auth/google`, User only). Both get the same stateless signed JWT; "Authentication reads no database per request" (API-site overview.md "Two kinds of caller"). Since 1.1.0+ `ActorLivenessFilter` does one indexed read per authenticated request to refuse deleted/restricted identities (API-site architecture.md). |

**Roles hierarchy (API-req Vision §8):** System Admin → manages all scopes, persons, applications;
Scope Admin → manages users & applications in owned scopes, adds co-owners (create new ScopeAdmin or
promote a User of the scope, UC-23); User → authenticate, view own profile, recover password, verify
email.

**JWT claims** (API-site flows/login.md "What the token carries"): `id` (PublicId, everyone),
`roleId` (everyone), `scopeId` (User only), `ownedScopeIds` (ScopeAdmin, comma-separated),
`scopePermissions` (JSON array, when the scope has flagged permissions), `mfaPending` (challenge
tokens only); plus `subjectRightsOnly` for restricted sign-ins (API-site architecture.md).

**Requirement ID conventions** (API-site requirements/_index.md): `FR-XX-nn`, `NFR-nn`, `UC-nn`,
`AF-nna`; groups SC, PE, RO, AU, PR, EV, AP, GO, SP, 2F, HC (and SR in SRD §3.8a). UI uses
`FR-AU/SC/PE/AP/PM/GU/UX`, `NFR`, `UI-nn`, `P-nn` (UI-req SRD §1.2; Use Case doc §1.5).

---

## 3. Architecture

### 3.1 API projects and layers (API-site architecture.md "The layers"; API/CONTRIBUTING.md "Project structure")

| Project | Path | Responsibility |
| --- | --- | --- |
| `ArturRios.Heimdall.Domain` | `src/Domain/` | Entities + `Roles` enum; depends on nothing |
| `ArturRios.Heimdall.Command` | `src/Application/` | Write side: commands, FluentValidation validators, handlers, services (token, 2FA, email verification), auditing decorator |
| `ArturRios.Heimdall.Query` | `src/Application/` | Read side: queries, validators, handlers, health checks, output DTOs |
| `ArturRios.Heimdall.Shared` | `src/Application/` | Messages + status-code maps, `IScopeOwnershipChecker`, `IActorAccessor` |
| `ArturRios.Heimdall.Data` | `src/Infrastructure/` | `AppDbContext`, entity maps, migrations, `DatabaseSeeder` |
| `ArturRios.Heimdall.WebApi` | `src/Presentation/` | Controllers, JWT issue/validate, filters, email + Google adapters, start-up |
| (`tools/ArturRios.Heimdall.OpenApiGen/`) | | Writes `docs/openapi/heimdall.json`; not in the solution |

Solution: `src/ArturRios.Heimdall.sln`. Tests mirror `src/` (unit + functional) (API/CONTRIBUTING.md).

- **CQRS**: `CommandMediator.ExecuteCommandAsync` / `QueryMediator.ExecuteQueryAsync` /
  `ExecutePaginatedQueryAsync` (from `ArturRios.Mediator`); handlers return `DataOutput<T>` or
  `PaginatedOutput<T>`; `ToActionResult` maps message → HTTP status via per-area `*MessageMap`
  (API-site architecture.md "CQRS: two mediators"; "How a failure becomes a status").
- **Auditing**: every write handler registered via `AddAuditedCommandHandler` → `AuditingCommandHandler`
  decorator writes one `AuditLog` row (NFR-09) (API-site architecture.md "Auditing by decoration";
  flows/audit-logging.md).
- **Request pipeline**: Forwarded headers (trusted proxies) → HTTPS redirect → TraceActivityMiddleware
  → ExceptionMiddleware → CORS → AuthenticationMiddleware → Rate limiter → MfaPendingGuardFilter →
  SubjectRightsOnlyGuardFilter → ActorLivenessFilter → RoleRequirement/AllowAnonymous → Controller →
  Mediator → Handler → PostgreSQL; metrics branch on its own port ahead of everything
  (API-site architecture.md "The HTTP request pipeline").
- **Authorization**: `[RoleRequirement]` attributes + `IScopeOwnershipChecker` inside handlers
  (API-site architecture.md "Authorization"); full matrix = API-req SRD §7.
- **Persistence**: repository interfaces `IAsyncRepository<T, long>` / `IAsyncReadOnlyRepository<T, long>`;
  single-use state spent by conditional `UPDATE` via `IAtomicWrites` (NFR-27) (API-site
  architecture.md "Persistence", "Single-use state").
- **Data store**: PostgreSQL only, every environment incl. tests (Testcontainers); EF Core code-first,
  snake_case singular names; entities in schema `heimdall` (API-req Technology Stack §4–5; API/README.md
  "Naming the login"). Data Protection key ring kept in the DB (NFR-06).
- **Response envelopes**: `DataOutput<T>` `{data, messages, errors, success}`; `PaginatedOutput<T>`
  adds `pageNumber, pageSize, totalRecords` (API-site api-reference.md "Response shape").

### 3.2 External integrations

| Integration | What | Config | Source |
| --- | --- | --- | --- |
| **Mailgun** (US region, via `ArturRios.Messaging`) | Verification, password reset, 2FA email codes, sign-up confirmation | `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_API_VERSION`, `MAILGUN_FROM`; unset → tokens logged (non-Production) / start-up fails (Production) | API-site operations.md "Integrations"; environments-and-deployment.md |
| **Google Identity** | ID-token verification (`Google.Apis.Auth`), validated offline against cached public certs; token never sent to Google | `HEIMDALL_GOOGLE_CLIENT_IDS`; unset → every Google token refused 401 | API-site operations.md "Google Sign-In"; API/README.md "#123" |
| **Prometheus** (OpenTelemetry exporter) | `/metrics` on port 9464 only | `HEIMDALL_METRICS_PORT` | API-site operations.md "Metrics — Prometheus" |
| **MEGA** | Daily encrypted off-server DB backups, 35 days | (hosting, not app config) | API-req Operations & Infrastructure §0.1 |
| **yggdrasil** (Jenkins, Traefik, console) | Deploys dev/hml/prod on one VPS | `/etc/yggdrasil/<env>/heimdall-api.env` | API/CONTRIBUTING.md "Where this is deployed from" |

Sub-processor list: Mailgun (Sinch, US), Hosting provider (Brazil), MEGA (Europe/adequate country)
(API-req Data Processing Agreement §7). Data hosted in **Brazil** (API-req Ops & Infra §0).

### 3.3 UI architecture (UI/CONTRIBUTING.md "Project structure"; UI-req Technology Stack §2–4)

| Path | Responsibility |
| --- | --- |
| `lib/app/` | App root, router + guard, themes (`app_version.dart`, `router.dart`, `route_access.dart`, `theme.dart` …) |
| `lib/core/` | Config, HTTP + interceptors (`network/auth_interceptor.dart`, `dio_client.dart`, `envelope.dart`), result model, token storage, scope source |
| `lib/features/<feature>/{data,domain,presentation}/` | Features: `applications, auth, data_rights, google_users, health, home, permissions, persons, privacy, profile, scopes` (directory listing) |
| `lib/shared/` | Feature-agnostic widgets — adaptive shell, breakpoints, forms |
| `packages/heimdall_api_client/` | **Generated** API client, never hand-edited |
| `api/heimdall.json` | Vendored snapshot of the API's OpenAPI spec |
| `tool/` | `refresh_openapi.dart`, `generate_api_client.dart`, `refresh_privacy_notice.dart` |
| `assets/privacy/` | Verbatim copy of the API's Privacy Notice, shown at `/privacy` |

- **State/DI**: `flutter_riverpod` ^3.4.3 (`Notifier`/`AsyncNotifier` back session + theme). Riverpod
  auto-retry disabled app-wide (UI/CHANGELOG.md 1.1.0).
- **Routing**: `go_router` ^18.0.2, single redirect guarding every route by session and role; web
  routes on path, not hash (UI/CHANGELOG.md 1.0.1).
- **HTTP**: one `dio` ^5.11.1 instance shared by every generated client, carrying the bearer-token
  interceptor; `retrofit` runtime.
- **Generated client**: `swagger_parser` ^1.45.0 + `build_runner` + `json_serializable` +
  `retrofit_generator` from `api/heimdall.json` → clients `AuthClient`, `ScopeClient`, `PersonClient`,
  `ApplicationClient`, `ScopePermissionClient`, `GoogleUserClient`, `HealthCheckClient`, each
  `AuthClient(dio)`; entry point `package:heimdall_api_client/export.dart` (UI-req Technology Stack §4.1).
  Presentation never imports the generated package; only `data/` does (UI/CONTRIBUTING.md).
- **Storage**: `flutter_secure_storage` ^11.2.0 for the token (Keystore / DPAPI / libsecret /
  WebCrypto-encrypted local storage); `shared_preferences` only for theme mode; challenge token never
  stored (UI-req Technology Stack §3; Ops & Infra §9).
- **Layout**: Material 3; breakpoints compact `< 600`, medium `600 – 1024`, expanded `> 1024`; bottom
  bar / rail / extended rail (UI-req SRD FR-UX-01, NFR-01).

### 3.4 How the UI talks to the API

- Base URL is compiled in at build time via `--dart-define` (`HEIMDALL_API_BASE_URL`, default
  `http://localhost:8080`) (UI/README.md "Configure").
- On the VPS the UI calls the API **under its own origin**: Traefik routes `/api/` on the UI host
  (`heimdall[-dev|-hml].example.com`) to that environment's API → no CORS needed. Locally UI is on
  `http://localhost:8081`, API on `http://localhost:8080`, and the API's `docker/local.env.example`
  lists `http://localhost:8081` in `HEIMDALL_CORS_ALLOWED_ORIGINS` (UI/README.md "Environments";
  API-site environments-and-deployment.md).
- Bearer token on every authenticated request; any `401` clears the session (UI-req SRD FR-AU-07/08).
- **Target scope**: on web the calling application writes `sessionStorage.setItem('heimdall.scopeId',
  '<scope-public-id>')`; `HEIMDALL_SCOPE_ID` is the fallback (desktop/Android or direct open)
  (UI/README.md "The target scope"; UI-req Ops & Infra §2.1). In code the scope source is read in
  `exchangeGoogleIdToken` (Google sign-in) — see §10 for password login.
- Errors are shown "as returned" from the envelope's `errors` array (UI-req SRD FR-UX-05).

### 3.5 How other systems (e.g. Fortuna) consume Heimdall — only what the sources say

- Client systems "authenticate users, query persons" (API-req Vision §5 C4 context).
- **Shared JWT secret**: in each VPS environment `HEIMDALL_AUTH_TOKEN_SECRET` — "fortuna-api in the
  same environment is given the same value" (API-site environments-and-deployment.md, step 4 table),
  i.e. Fortuna validates Heimdall JWTs with the same signing secret. Issuer/audience default to
  `heimdall` in `docker-compose.yml` (`HEIMDALL_AUTH_TOKEN_ISSUER`/`_AUDIENCE: ${…:-heimdall}`).
- **Scope permissions in the JWT**: a client system reads permission names from the
  `scopePermissions` claim (API-site flows/scope-permission-claims.md).
- **Trusted caller key** (API 1.4.0): "A client system such as Fortuna's API signs its users in on
  their behalf", so it sends `X-Heimdall-Caller-Key` (one of `HEIMDALL_TRUSTED_CALLER_KEYS`, ≥32
  chars each) and `X-Heimdall-Client-Address` (end user's IP; IPv6 by /64) to get per-user
  anonymous-auth rate-limit buckets. Headers "authenticate nobody and open no endpoint"; send only
  server-side over TLS (API-site operations.md "A client system calling for its users";
  API/CHANGELOG.md 1.4.0).
- **Per-scope email links** (API 1.4.0, FR-SR-10): `PUT /api/scopes/{id}/email-links` so "a client
  system such as Fortuna can send its users to its own `/verify-email` and `/password-reset` screens";
  those screens post the token back to `POST /api/auth/verify-email` / `POST /api/auth/password-reset`
  (API-site operations.md "Pointing a scope at a client application's screens").
- **Scope ID handoff**: UI 1.5.0 shows the scope's ID with a copy button — "A calling application
  passes this ID to Heimdall to create and authenticate its users" (UI/CHANGELOG.md 1.5.0).
- Login for a `User` must name the scope (`ScopeId` in `LoginCommand`: present → User lookup in that
  scope; absent → ScopeAdmin/SystemAdmin) (API `src/Application/ArturRios.Heimdall.Command/Input/LoginCommand.cs`
  doc comment; API-site flows/login.md).
- Server-to-server callers are unaffected by CORS (API-site operations.md "Cross-origin requests").

### 3.6 Diagram material

**(a) Component graph** — nodes: Client systems (e.g. Fortuna API) / Heimdall UI (web, Windows,
Linux, Android) → Heimdall API (WebApi → Command/Query → Shared/Domain → Data) → PostgreSQL;
API → Mailgun; UI → Google Identity (obtain ID token); API verifies Google ID token offline;
Prometheus scrapes API:9464; MEGA holds backups. Basis: API-site overview.md "What the API is
composed of"; UI-req Vision §5 C4; API-site operations.md.

**(b) Deployment/environments** (API/README.md "Deploy with Docker"; UI/README.md "Environments"):

| Env | Where | Deployed by | API `ASPNETCORE_ENVIRONMENT` | API host | UI host | DB |
| --- | --- | --- | --- | --- | --- | --- |
| `local` | Developer's Windows machine, Docker Desktop | By hand | `Development` | `http://localhost:8080` | `http://localhost:8081` | `heimdall_local` (PostgreSQL on Windows) |
| `development` | VPS, on demand | Jenkins on push to `develop` | `Development` | `heimdall-api-dev.example.com` + `/api/` under `heimdall-dev.example.com` | `https://heimdall-dev.example.com` | `heimdall_development` |
| `homologation` | VPS, on demand | Jenkins on push of `release/x.y.z` | `Staging` | `heimdall-api-hml.example.com` + `/api/` under `heimdall-hml.example.com` | `https://heimdall-hml.example.com` | `heimdall_homologation` |
| `production` | VPS, always on | Jenkins on green `release/x.y.z → main` PR (then merges + tags) | `Production` | `heimdall-api.example.com` + `/api/` under `heimdall.example.com` | `https://heimdall.example.com` | `heimdall` |

`example.com` stands for the real domain (both READMEs). One Ubuntu VPS, one Docker engine, one
PostgreSQL instance; Traefik with wildcard cert; Compose project `heimdall-api-<environment>`; network
alias `heimdall-api.<environment>`; `edge` and `telemetry` networks (API-site
environments-and-deployment.md). `PUBLIC_HOST` (API host) serves "the mobile and desktop clients";
`UI_HOST` + `/api/` serves the browser build (same page, "How yggdrasil deploys it").

**(c) Login + 2FA sequence summary** (API-site flows/login.md; flows/two-factor.md; api-reference.md):
1. Client `POST /api/auth/login {email, password, scopeId?}` (anonymous, rate-limited 10/min/IP).
2. Validate (400 on shape, AF-11f) → look up person (User by email within scope; admins by email) →
   Argon2id verify (decoy hash for unknown address) → eligibility (`TryBuildSubject`). Unknown email,
   wrong password, deleted person, deleted scope, ScopeAdmin with no live scope, lockout → all
   "invalid credentials" (AF-11a…e, FR-AU-09).
3. If active 2FA (AF-11g): if email method enabled, retire live codes and mail a fresh one; answer
   `200 {requiresTwoFactor, challengeToken, availableMethods}`.
4. Else: issue JWT (fold flagged scope permissions) → `200 {token, expiresAt, emailVerified}`; audit row.
5. Challenge: `POST /api/auth/2fa/verify` with `challengeToken` in body + app code / email code /
   recovery code → full token. `POST /api/auth/2fa/challenge/resend` re-mails the email code (UC-46).
6. Restricted identity: `200` with `processingRestricted: true` + subject-rights-only token (1.3.0).
UI side: UI-01 → AF-01c moves session to `challenged` → `/login/two-factor` (UI-02) → session stored
in secure storage (UI-req Use Case doc UI-01/UI-02).

**(d) Role-based UI**: see the authorization matrix in §5.3 (UI-req SRD §4).

---

## 4. Install / run

### 4.1 API prerequisites (API/README.md "Prerequisites"; API/CONTRIBUTING.md)

- **.NET 10 SDK**; **PostgreSQL**; **Python 3** (migration menu and helper scripts); **Docker**
  (Compose deploy; functional tests via Testcontainers).
- Pinned EF Core CLI: `dotnet tool restore` (`.config/dotnet-tools.json`: `dotnet-ef` `10.0.12`).
- Clone with submodules (docs theme): `git clone --recurse-submodules https://github.com/artur-rios/heimdall-api.git`
  (API-site getting-started.md "Clone").
- Docs site preview: Hugo Extended 0.160.1+, Node.js 24+, Dart Sass 1.95.0+; `git submodule update
  --init --recursive`, `npm run install:theme-deps --prefix docs/themes/docsy`, `hugo -s docs server`
  (API/CONTRIBUTING.md "Documentation site").

### 4.2 API configuration (names only)

Template: `src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env` → copy to `.env.local`
(`cp src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env.local`).
`ASPNETCORE_ENVIRONMENT` selects `Environments/.env.<local|development|staging|production>` and
`Settings/appsettings.<Env>.json`; missing file falls back to `Local` (API-site getting-started.md).

- **Required**: `HEIMDALL_DATA_CONNECTIONSTRING`, `HEIMDALL_DATA_DATABASETYPE` (`PostgreSql`),
  `HEIMDALL_AUTH_TOKEN_SECRET`, `HEIMDALL_MASTER_USER_NAME` / `_EMAIL` / `_PASSWORD`.
- **Auth/tokens**: `HEIMDALL_AUTH_TOKEN_ISSUER` / `_AUDIENCE`, `HEIMDALL_AUTH_TOKEN_EXPIRATION_IN_SECONDS`
  (3600), `HEIMDALL_AUTH_TOKEN_SECRET_PREVIOUS` (rotation), `HEIMDALL_AUTH_MAX_CONCURRENT_PASSWORD_HASHES` (4),
  `HEIMDALL_EMAIL_VERIFICATION_TOKEN_EXPIRATION_IN_SECONDS` (86400), `HEIMDALL_PASSWORD_RESET_TOKEN_EXPIRATION_IN_SECONDS` (3600).
- **Network**: `HEIMDALL_CORS_ALLOWED_ORIGINS`, `HEIMDALL_TRUSTED_PROXIES`, `HEIMDALL_TRUSTED_CALLER_KEYS`,
  `HEIMDALL_METRICS_PORT` (9464; 0 = off).
- **Integrations**: `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_API_VERSION` (v3), `MAILGUN_FROM`,
  `HEIMDALL_EMAIL_VERIFICATION_URL`, `HEIMDALL_PASSWORD_RESET_URL`, `HEIMDALL_GOOGLE_CLIENT_IDS`.
- **Data/TLS**: `HEIMDALL_DATA_REQUIRE_TLS` (false).
- **Retention**: `HEIMDALL_RETENTION_TOKEN_GRACE_DAYS` (7), `_PURGE_INTERVAL_MINUTES` (60),
  `_PURGE_BATCH_SIZE` (500), `_PURGE_ENABLED` (true), `_ERASURE_DEADLINE_DAYS` (30),
  `_DELETION_WINDOW_DAYS` (90), `_ANONYMISATION_ENABLED` (true), `_AUDIT_ACTOR_DAYS` (548),
  `_AUDIT_PSEUDONYMISATION_ENABLED` (true), `_LOG_DAYS` (365) — all prefixed `HEIMDALL_RETENTION_`.
- **Monitoring**: `HEIMDALL_MONITORING_ENABLED` (true), `_WINDOW_MINUTES` (15), `_REFUSAL_THRESHOLD`
  (20), `_LOCKOUT_THRESHOLD` (10); `HEIMDALL_LOG_DIRECTORY` (`logs`).
- **Container-only (Compose)**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
  `DB_SEARCH_PATH` (`public`), `DB_CONNECTION_EXTRA`, `API_PORT` (8080), `API_IMAGE`, `API_IMAGE_TAG`,
  `HEIMDALL_RUN_MIGRATIONS` (true), `COMPOSE_PROJECT_NAME`; VPS templates add `PUBLIC_HOST`, `UI_HOST`
  (`API/docker-compose.yml`; API-site environments-and-deployment.md).
- **Signal collector script**: `HEIMDALL_SIGNAL_ALERT_TO`, `HEIMDALL_SIGNAL_ALERT_FROM`,
  `HEIMDALL_SIGNAL_STATE_FILE`, `MAILGUN_API_BASE_URL` (API-site operations.md).

Full table: API-site operations.md "Environment variables at a glance".

### 4.3 API commands

| Task | Command | Source |
| --- | --- | --- |
| Migrations (list/create/apply) | `python scripts/migrations.py` | API/README.md "Migrations" |
| Run from source | `dotnet run --project src/Presentation/ArturRios.Heimdall.WebApi` → `http://localhost:5177` (http profile), `https://localhost:7235` (https) | API/README.md "Run" |
| Swagger UI (non-Production) | `http://localhost:5177/swagger` | same |
| Build | `dotnet build src/ArturRios.Heimdall.sln` | API/CONTRIBUTING.md |
| Tests | `dotnet test src/ArturRios.Heimdall.sln` (`--filter "Category=Unit"` / `"Category=Functional"`) | same |
| Coverage | `python scripts/coverage.py` (floor 90% line) | same; API-req Testing Spec §2.1 |
| OpenAPI regen | `python scripts/openapi.py` | same |
| Local Docker | `cp docker/local.env.example docker/local.env` then `docker compose --env-file docker/local.env up -d --build` → `http://localhost:8080` | API/README.md "Deploy with Docker" |
| Day-to-day (local) | `docker compose --env-file docker/local.env logs -f api` / `ps` / `down` | API-site environments-and-deployment.md §7 |
| VPS env on/off | `scripts/ygg.sh env start <environment>` / `env stop` / `env status` / `config heimdall-api` (on the VPS) | same |
| Bruno collection | `npx @usebruno/cli run Auth --env Local` | API-site getting-started.md |

Container: multi-stage (`mcr.microsoft.com/dotnet/sdk:10.0` → `mcr.microsoft.com/dotnet/aspnet:10.0`),
non-root `$APP_UID`, `ASPNETCORE_HTTP_PORTS=8080;9464`, `EXPOSE 8080 9464`, entrypoint
`/usr/local/bin/entrypoint.sh` applies the EF migrations bundle then starts the API; Compose
healthcheck `curl --fail --silent http://localhost:8080/healthcheck` (interval 15s, retries 5, start
period 30s); named volume `logs:/app/logs` (`API/Dockerfile`; `API/docker-compose.yml`).
Seeder creates the three roles and the master System Admin on an empty DB (API-site getting-started.md "Run").
First four calls on an empty DB: Login → Create an administrator → Create a scope → Create a User in
a scope (API-site getting-started.md "Calling the API").

### 4.4 UI prerequisites and config (UI/README.md "Prerequisites", "Configure")

- **Flutter 3.47.7** or newer, stable (Dart 3.13.5) (UI-req Technology Stack §2).
- Web: Chromium browser. Windows: Visual Studio / Build Tools, "Desktop development with C++" **and
  C++ ATL**. Linux: `clang`, `cmake`, `ninja-build`, `pkg-config`, `libgtk-3-dev`, `liblzma-dev`,
  `libstdc++-12-dev`, `libsecret-1-dev`. Android: SDK + `cmdline-tools`, API 37 platform
  (`sdkmanager --install "platforms;android-37.0"`), licences, JDK 17; `compileSdk = 37`.
- `flutter doctor`; `git clone https://github.com/artur-rios/heimdall-ui.git`; `flutter pub get`.
- Build-time keys: `HEIMDALL_API_BASE_URL` (default `http://localhost:8080`),
  `HEIMDALL_GOOGLE_CLIENT_ID` (unset hides Google control), `HEIMDALL_SCOPE_ID`. Local file:
  `cp config/local.json.example config/local.json` (git-ignored), used with
  `--dart-define-from-file=config/local.json`.
- **Values are public**: compiled into the JS bundle — never pass a secret (UI/README.md warning).

### 4.5 UI run / build per target (UI/README.md "Run", "Build")

| Target | Run | Build | Artifact |
| --- | --- | --- | --- |
| Web | `flutter run -d chrome --web-port 8081 --dart-define-from-file=config/local.json` | `flutter build web --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com` | `build/web` (host must fall back to `index.html`) |
| Windows | `flutter run -d windows --dart-define-from-file=config/local.json` | `flutter build windows --release --dart-define=…` | `build/windows/x64/runner/Release` |
| Linux | `flutter run -d linux --dart-define-from-file=config/local.json` | `flutter build linux --release --dart-define=…` | `build/linux/x64/release/bundle` |
| Android | `flutter run -d android --dart-define-from-file=config/local.json` | `flutter build apk --release --dart-define=…` (or `appbundle`) | `build/app/outputs/flutter-apk` (bundle: `build/app/outputs/bundle/release`) |

UI web container (`UI/Dockerfile`; README "Container image (web)"): build stage `debian:trixie-slim`
with Flutter `3.47.7` (+ `FLUTTER_SHA256`), serve stage `nginxinc/nginx-unprivileged:alpine`, non-root,
port **8080**, deep-link fallback, `/healthz` probe, config `docker/nginx.conf`. Build args
`HEIMDALL_API_BASE_URL` (required), `HEIMDALL_GOOGLE_CLIENT_ID`, `HEIMDALL_SCOPE_ID`,
`FLUTTER_VERSION`/`FLUTTER_SHA256`. Example: `docker build -t heimdall-ui:web --build-arg …` then
`docker run --rm -p 8080:8080 heimdall-ui:web`. One image per environment (values baked in).

UI tests/gate: `dart format --set-exit-if-changed . && flutter analyze && flutter test`; also
`flutter test integration_test`, `flutter test --coverage` (UI/CONTRIBUTING.md "Test").
Client regen: `dart run tool/refresh_openapi.dart ../heimdall-api/docs/openapi/heimdall.json` then
`dart run tool/generate_api_client.dart` (UI/CONTRIBUTING.md "Generated API client").

### 4.6 Where release artifacts come from (exact)

**API**
- GitHub releases `v1.0.0` … `v1.4.0` exist with **no assets** (`gh release view` → `assets: []`);
  created by Jenkins on production deploy; notes "generated from the pull requests merged since the
  previous tag"; `CHANGELOG.md` is the curated record (API/CONTRIBUTING.md "Releasing", "Versioning").
- Container image: built **by Jenkins on the VPS** (yggdrasil), tagged `1.4.0-<short commit>`
  (API/CONTRIBUTING.md "Versioning"); image tags start with `<environment>-` per environment
  (API-site environments-and-deployment.md alert). Compose image name default
  `${API_IMAGE:-heimdall-api}:${API_IMAGE_TAG:-latest}`. **No workflow pushes an image to a
  registry**: `tests.yml` job `docker` builds with `docker/build-push-action` and `push: false`
  ("Build only, no push and no run").
- GitHub Actions (`API/.github/workflows/`): `tests.yml` (Tests: push/PR; restore, vulnerabilities
  script, build Release, Unit + Functional, coverage report artifact; calls `build-docs.yml` on push
  to `main`; docker build-only job), `build-docs.yml` (Build Docs: push to `main` touching `docs/**`,
  `CHANGELOG.md`, `CONTRIBUTING.md`; `workflow_call`; `workflow_dispatch`; Hugo extended `latest`,
  Node 24, Dart Sass 1.105.1 → GitHub Pages), `check-openapi.yml` (`python3 scripts/openapi.py --check`),
  `branch-policy.yml` (PRs into develop/main).
- Jenkinsfile: `develop` → development; `release/x.y.z` → homologation; PR `release/x.y.z → main` →
  production, merge, tag `vx.y.z`, delete branch; "Build and test stay in GitHub Actions; this file
  only deploys" (`API/Jenkinsfile`).

**UI**
- GitHub releases `v1.0.0` … `v1.6.1` exist with **no assets** (`gh release view -R artur-rios/heimdall-ui`).
- `build.yml` (Build: push to `main` + `workflow_dispatch`, `FLUTTER_VERSION: 3.47.7`) uploads
  **workflow artifacts** `heimdall-ui-web` (`build/web`), `heimdall-ui-linux`
  (`build/linux/x64/release/bundle`), `heimdall-ui-windows` (`build/windows/x64/runner/Release`),
  `heimdall-ui-android` (`build/app/outputs/flutter-apk/*.apk`). No API base URL supplied (default
  kept out of public logs). APK "Signed with the debug key: suitable for testing, never for release".
- Web container image built and deployed by Jenkins per environment, tagged `<environment>-<version>`
  (UI/README.md warning; UI-req Ops & Infra §2.2); CONTRIBUTING says release branch deployed as image
  tag `1.4.0-<short commit>`.
- Other workflows: `ci.yml` (push main/develop + PRs: format, analyze, test), `check-api-client.yml`
  (regenerate + diff), `branch-policy.yml` (also checks `pubspec.yaml` version = release version).
- Jenkinsfile: `yggdrasilPipeline(stack: 'heimdall-ui')`, same branch→environment mapping.

---

## 5. Usage — UI use cases and screens

Source: UI-req Use Case Specification Document §1.4 (inventory, traces), headings `### UI-nn`
(actors), UI/README.md "Use case status".

### 5.1 By group (actor → one-liner; API UC traced)

**Authentication & Session**
- UI-01 Login — Anonymous; email + password via `POST /api/auth/login`; branches to 2FA (UC-11).
- UI-02 Complete two-factor challenge at login — Anonymous holding a challenge; code or recovery code (UC-38).
- UI-03 Request password recovery — Anonymous; same confirmation whether or not registered (UC-12).
- UI-04 Reset password — Anonymous; token from `/password-reset?token=…` link (UC-13).
- UI-05 Verify email and resend verification — Anonymous or any authenticated; `/verify-email?token=…`; resend prompt (UC-14, UC-15).
- UI-06 Sign in and sign out with Google — Anonymous, Google User; when a client id is configured (UC-25, UC-26).
- UI-07 Guard routes by session and role — All; role-appropriate destinations, 401 → sign-in (—).
- UI-30 Use a restricted session — Restricted subject (any role or Google User); `/restricted` with Lift restriction, Download my data (JSON), Request erasure, Sign out (UC-11 AF-11i, UC-25 AF-25e, UC-38, UC-41, UC-42, UC-45; UI/CHANGELOG.md 1.4.0).

**Profile & Security** (System Admin, Scope Admin, User)
- UI-08 View and edit own profile (UC-07, UC-08).
- UI-09 Manage two-factor authentication — enable (QR of `otpAuthUri` + secret text), confirm, recovery codes shown once, disable, regenerate (UC-36, UC-37, UC-39, UC-40).

**Scope Management**
- UI-10 Browse and search scopes — System Admin, Scope Admin (UC-02).
- UI-11 Create a scope — System Admin; at least one owner; "Add me" (UC-01; UI 1.3.0).
- UI-12 View and update a scope — System Admin, Scope Admin (read-only for Scope Admin per SRD §4) (UC-02, UC-03).
- UI-13 Delete a scope, logically and permanently — System Admin (UC-04, UC-05).
- UI-14 Manage scope owners — add existing, create new co-owner, promote User, remove (UC-21, UC-22, UC-23).
- UI-15 Toggle Google Sign-In for a scope — System Admin, Scope Admin (UC-24).

**Person Management** (System Admin, Scope Admin)
- UI-16 Browse and search persons in a scope (UC-07).
- UI-17 Create a person (UC-06); System Admin can create a no-scope person via `POST /api/persons` (FR-PE-04).
- UI-18 View and update a person (UC-07, UC-08).
- UI-19 Delete a person — Scope Admin logical only (UC-09, UC-10).

**Application Management** (System Admin, Scope Admin)
- UI-20 Browse applications in a scope (UC-17); UI-21 Create (UC-16); UI-22 View and update (UC-17, UC-18); UI-23 Delete — Scope Admin logical only (UC-19, UC-20).

**Scope Permission Management** (System Admin, Scope Admin)
- UI-24 Browse (UC-32); UI-25 Create (UC-31); UI-26 View and update, incl. JWT-claim flag (UC-32, UC-33); UI-27 Delete — Scope Admin logical only (UC-34, UC-35).

**Google Users** (System Admin, Scope Admin)
- UI-28 Browse and view Google users (read-only detail, initials avatar fallback) (UC-27).
- UI-29 Delete a Google user — Scope Admin logical only (UC-28, UC-29).

**Platform items** (UI-req Use Case doc §1.5): P-01 scaffolding; P-02 generated API client + drift
check; P-03 multi-platform build and release pipelines; P-04 API health and diagnostics screen
(consumes UC-30).

**Conventions**: destructive actions need a confirmation naming the record; permanent deletion
requires typing the record's name (email for persons/Google users) (UI-req Use Case doc §1.6; SRD FR-*-07/08).

**Additional UI features from changelog**: home dashboard with own-account status and admin overview
of first ten scopes, version footer "Heimdall UI v1.6.x" (1.6.0); read-only until **Edit** (1.6.0);
scope ID copy button, favicon/app icons (1.5.0); `/privacy` page showing the API's Privacy Notice
verbatim (1.2.0); Bitwarden/password-manager compatible sign-in form on web (1.5.1, 1.6.1).

### 5.2 Screens (UI-req SRD §3 "Screen inventory"; matches `UI/lib/app/router.dart`)

`/login` (UI-01, UI-06) · `/login/two-factor` (UI-02) · `/password-recovery` (UI-03) ·
`/password-reset` (UI-04) · `/verify-email` (UI-05) · `/restricted` (UI-30) · `/` Home (UI-07) ·
`/profile` (UI-08) · `/profile/security` (UI-09) · `/scopes` (UI-10) · `/scopes/new` (UI-11) ·
`/scopes/:scopeId` (UI-12, 13, 15) · `/scopes/:scopeId/owners` (UI-14) · `/scopes/:scopeId/persons`
(UI-16) · `/scopes/:scopeId/persons/new` (UI-17) · `/scopes/:scopeId/persons/:personId` (UI-18, 19) ·
`/scopes/:scopeId/applications` (UI-20) · `…/applications/new` (UI-21) ·
`…/applications/:applicationId` (UI-22, 23) · `/scopes/:scopeId/permissions` (UI-24) ·
`…/permissions/new` (UI-25) · `…/permissions/:permissionId` (UI-26, 27) ·
`/scopes/:scopeId/google-users` (UI-28) · `…/google-users/:googleUserId` (UI-29) · `/health` (P-04) ·
`/privacy` (issue #73). Router also has `/not-available` (role cannot reach) and a not-ready fallback.

### 5.3 Role-based UI matrix (UI-req SRD §4, condensed)

| Screen | System Admin | Scope Admin | User | Anonymous |
| --- | --- | --- | --- | --- |
| Sign in, recovery, reset, verification | — | — | — | Full |
| Privacy notice | Full | Full | Full | Full |
| Second-factor challenge | Full | Full | Full | Held challenge only |
| Restricted session | Restricted only | Restricted only | Restricted only | Hidden |
| Home; own profile & security | Full | Full | Full | Hidden |
| Scope listing / detail / owners / Google Sign-In toggle | All scopes | Owned scopes only | Hidden | Hidden |
| Create scope; delete scope (logical/permanent) | Full | Hidden | Hidden | Hidden |
| Scope update (name, description) | Full | Read-only | Hidden | Hidden |
| Persons / applications / permissions: list, create, update, logical delete | Full | Owned scopes only | Hidden | Hidden |
| Google users: list, detail, logical delete | Full | Owned scopes only | Hidden | Hidden |
| Any permanent delete (person, application, permission, Google user) | Full | Hidden | Hidden | Hidden |
| Health and diagnostics | Full | Read-only | Hidden | Hidden |

A restricted session gets only `/restricted` and `/privacy`, whatever its role (SRD §4 note; FR-AU-22).

---

## 6. API surface summary

### 6.1 Endpoint groups and counts (counted from `[Http*]` attributes in
`API/src/Presentation/ArturRios.Heimdall.WebApi/Controllers/*.cs`; the committed
`API/docs/openapi/heimdall.json` has the same **61 operations**)

| Group (controller, route) | Count | Endpoints |
| --- | --- | --- |
| Auth — `api/auth` (`AuthController`) | 21 | `POST login, password-recovery, register, password-reset, verify-email, resend-verification, google, google/sign-out, 2fa/enable, 2fa/confirm, 2fa/verify, 2fa/challenge/resend, 2fa/disable, 2fa/recovery-codes/regenerate, data-export, erasure-request, processing-restriction, erasure-reconciliation, processing-restriction/lift`; `GET erasure-requests, 2fa` |
| Scopes — `api/scopes` | 9 | `POST /`; `GET /`, `GET /{id}`; `PUT /{id}`, `/{id}/google-signin`, `/{id}/self-registration`, `/{id}/email-links`; `DELETE /{id}`, `/{id}/hard` |
| Persons — `api` | 13 | `POST persons`, `scopes/{scopeId}/persons`, `scopes/{scopeId}/owners`, `scopes/{scopeId}/owners/{personId}`, `scopes/{scopeId}/users/{personId}/promote`; `PUT persons/{id}`; `DELETE persons/{id}`, `persons/{id}/hard`, `scopes/{scopeId}/owners/{personId}`; `GET persons/{id}`, `scopes/{scopeId}/persons`, `scopes/{scopeId}/owners`, `persons/scope-admins` |
| Applications — `api/scopes/{scopeId}/applications` | 6 | CRUD + `/{id}/hard` |
| Scope permissions — `api/scopes/{scopeId}/permissions` | 6 | CRUD + `/{id}/hard` |
| Google users — `api/scopes/{scopeId}/google-users` | 4 | `GET /`, `GET /{id}`, `DELETE /{id}`, `DELETE /{id}/hard` |
| Health — `api/healthcheck` | 2 | `GET /api/healthcheck`, `GET /api/healthcheck/detailed` (root `/healthcheck` aliases not in OpenAPI) |
| **Total** | **61** | |

Who-may-call notation and per-endpoint use case: API-site api-reference.md. Anonymous credential
endpoints rate-limited 10/min per IP (IPv6 by /64); the 4 authenticated credential-checking ones
(`2fa/confirm`, `2fa/disable`, `2fa/recovery-codes/regenerate`, `erasure-request`) share it
(API-site api-reference.md; operations.md). `erasure-reconciliation` is the System-Admin step that
re-applies erasures after a restore (API-req Ops & Infra §0.1 "Restoring without undoing an erasure").

Callers: `api-client/` holds `.http` (JetBrains HTTP Client) and Bruno collections (API/README.md "Run").

### 6.2 Use case groups (API/README.md "Use case status"; API-req Use Case Specification Document)

| Group | Use cases | Count |
| --- | --- | --- |
| Scope Management | UC-01–05, UC-21–23 | 8 |
| Person Management | UC-06–10 | 5 |
| Authentication & Security | UC-11–15, UC-36–40, UC-46, UC-47 | 12 |
| Application Management | UC-16–20 | 5 |
| Scope Permission Management | UC-31–35 (delivered together, no issue links) | 5 |
| Google Sign-In | UC-24–29 | 6 |
| Data Subject Rights | UC-41–45 | 5 |
| Platform (health check) | UC-30 (specified in API-req Operations & Infrastructure §3.5) | 1 |

All marked ✅ in the README tracker. Platform items: scaffolding (#31), health check UC-30 (#32),
audit logging NFR-09 (#78), Mailgun delivery — all ✅. Project board:
https://github.com/users/artur-rios/projects/7 (API); https://github.com/users/artur-rios/projects/11
("Heimdall UI Delivery").

### 6.3 Milestones and status

API (README "Milestones" table, as written): MVP ✅ 18/18; Google Sign-In ✅ 6/6; LGPD & GDPR
Compliance 🚧 18/20. Live GitHub (`gh api …/milestones?state=all`, 2026-10-13): MVP open=0
closed=18; Google Sign-In open=0 closed=6; LGPD & GDPR Compliance **open=0 closed=39** (all three
milestones still in `open` state). See §10.

UI (live GitHub): Platform & Infrastructure 0/4 open; Authentication & Session 8 closed; Profile &
Security 2; Scope Management 6; Person Management 4; Application Management 4; Scope Permission
Management 4; Google Users 2 — all 0 open. README marks UI-01…UI-29 and P-01…P-04 ✅ and UI-30 🚧
(issue #103 is CLOSED on GitHub; shipped in UI 1.4.0).

---

## 7. Operations

- **Environments**: §3.6(b). Dev/hml run on demand; prod always on (`scripts/ygg.sh env stop
  production` refuses unless forced). Dev and hml hold no real personal data; tokens/2FA codes are
  logged there (API-req Ops & Infra §0.2; API-site environments-and-deployment.md).
  ASP.NET environment effects: Swagger served only in Development; developer exception page only in
  Development; EF parameter logging on except Production; e-mails without Mailgun logged
  (Dev/Staging) or start-up fails (Production) (environments-and-deployment.md table).
- **Health checks (UC-30)**: `GET /api/healthcheck` (anonymous liveness, no DB read) and
  `GET /api/healthcheck/detailed` (System Admin; per-dependency; aggregate Healthy only if all are,
  FR-HC-05); also at root `/healthcheck(/detailed)` for container health check and yggdrasil status
  page (API-site operations.md "Health checks — UC-30"; API/CHANGELOG.md 1.1.1). Response example
  `{"status":"Healthy","services":[{"name":"Database","status":"Healthy"}]}`. UI web image probe
  `/healthz` (UI/README.md). UI `/health` screen is P-04.
- **Metrics**: Prometheus text at `GET /metrics` on port 9464 only (never published; scraped as
  `heimdall-api.<environment>:9464` on `telemetry` network); OpenTelemetry meters for ASP.NET Core,
  HttpClient (Mailgun), runtime, Kestrel, EF Core, Npgsql; label `service_name="heimdall-api"`
  (API-site operations.md "Metrics — Prometheus").
- **Logging**: Serilog; console JSON + rolling files under `HEIMDALL_LOG_DIRECTORY`; EF diagnostics
  outside Production only; log files removed after `HEIMDALL_RETENTION_LOG_DAYS` (365); no log line
  writes an email address (`{EmailRef}` instead) (NFR-22); client IP of every request logged, kept 12
  months (API/CHANGELOG.md 1.1.0) (API-site operations.md "Logging").
- **Rate limiting / lockout**: fixed window 10 req/min per client IP on anonymous credential endpoints
  (429); per-account budgets — 10 failed passwords → 15-minute lockout; 5 guesses per email code;
  TOTP step single-use; challenge single redemption, 5 guesses (API-site operations.md "Rate limiting
  and lockout"). Trusted proxies / caller keys as in §3.5.
- **Security signals (NFR-26)**: `SecurityMonitoringService` writes `SECURITY_SIGNAL` warnings with
  kinds `REPEATED_REFUSALS`, `LOCKOUT_SPIKE`, `CREDENTIAL_VERIFICATION_SHEDDING`;
  `scripts/security_signals.py` mails new ones via Mailgun (`--stdout`, `--all`, `--quiet`; exit codes
  0/1/2), suggested cron every 15 min (API-site operations.md).
- **Data retention (NFR-19…22)**: hourly purge of expired single-use tokens (+7-day grace);
  anonymisation of deleted identities (30/90 days); audit attribution cleared after 18 months
  (DB trigger enforces); logs 12 months (API-site operations.md "Data retention — NFR-19";
  API-req Data Retention Schedule Document).
- **Encryption / backups (NFR-25)**: DB volume and backups encrypted (confirmed 10 Sep 2026); daily
  full backup to MEGA, client-side encrypted, 35 days; restore testing quarterly "⚠️ Proposed";
  `HEIMDALL_DATA_REQUIRE_TLS` for DB TLS (API-req Ops & Infra §0.1).
- **Signing-secret rotation**: set `HEIMDALL_AUTH_TOKEN_SECRET_PREVIOUS`, wait one token lifetime,
  clear it (API-site operations.md "Rotating the signing secret").
- **Scaling**: horizontally scalable (NFR-06); rate limiter window per instance; account budgets in DB
  (API-site operations.md "Scaling"). Set `HEIMDALL_RUN_MIGRATIONS=false` for >1 replica.
- **Performance targets**: NFR-05 100 ms median / 250 ms tail at 128 in-flight callers (non-password
  endpoints); NFR-18 password endpoints 347–491 ms median on reference config (API-req SRD §6).
- **Compliance documents** (API-req, all LGPD/GDPR): Data Retention Schedule Document; Data
  Protection Document (record of processing, LGPD Art. 37 / GDPR Art. 30; controller vs processor per
  scope — tenant is controller of its scope's persons, Heimdall processor; Heimdall controller of
  System Admins, audit log, logs, §3); Data Protection Impact Assessment (GDPR Art. 35, LGPD Art. 38);
  Privacy Notice (Version 1.2 — 5 October 2026; controller and Encarregado: Artur Rios; contact
  published in §2); Data Processing Agreement (LGPD Art. 39, GDPR Art. 28; sub-processor list §7; EU
  SCCs Module Two incorporated per API/README.md #124); Incident Response Document (ANPD 3 working
  days per Res. CD/ANPD nº 15/2024; GDPR Art. 33 72 hours; shorter governs); Threat Model Document
  (trust boundaries TB-1…TB-5, findings register). GDPR applies (Art. 3(2)) — determined
  10 September 2026 (API-req Data Protection Document §7.2; API/README.md "#124").
- **Process**: branching `feature/<name>`/`fix/<name>` → `develop` → `release/x.y.z` → `main` (tag
  `vx.y.z`); protected `develop`/`main`; Conventional Commits lowercase; SemVer with documented
  major/minor/patch rules; issue status Todo → In Progress → Testing → Done (API/CONTRIBUTING.md;
  UI/CONTRIBUTING.md; API-req Development Workflow Document §3). Yggdrasil console at
  `https://yggdrasil.<domain>` (or Android app) shows each environment's version, commit, deploy time,
  health.

---

## 8. Versions

| Item | Version | Source |
| --- | --- | --- |
| Heimdall API latest release | **v1.4.0** (GitHub release "Latest", 2026-10-13T15:34Z; CHANGELOG `[1.4.0] - 2026-10-13`) | `gh release list -R artur-rios/heimdall-api`; API/CHANGELOG.md |
| API releases | v1.0.0 (2026-09-28), v1.1.0, v1.1.1 (2026-10-09), v1.2.0 (2026-10-09), v1.3.0 (CHANGELOG 2026-10-11; GH release 2026-10-12T00:19Z), v1.4.0 | gh; CHANGELOG |
| Heimdall UI latest release | **v1.6.1** (GitHub release "Latest", 2026-10-12T16:30Z) | `gh release list -R artur-rios/heimdall-ui`; UI/CHANGELOG.md |
| UI releases | v1.0.0, v1.0.1 (2026-09-29), v1.1.0, v1.2.0, v1.3.0 (2026-10-09), v1.4.0, v1.5.0 (2026-10-11), v1.5.1, v1.6.0, v1.6.1 (2026-10-12) | same |
| UI in-app version | `pubspec.yaml` `version: 1.6.1`; `lib/app/app_version.dart` `appVersion = '1.6.1'` → "Heimdall UI v1.6.1" footer; releases up to v1.5.1 had template `1.0.0+1` | UI/CONTRIBUTING.md "Versioning" |
| UI ↔ API compatibility notes | UI 1.3.0 requires API 1.2.0 (System Admin owners); UI 1.4.0 (UI-30) requires API 1.3.0 | UI/CHANGELOG.md 1.3.0, 1.4.0 |
| OpenAPI document version | `v1` — the document's name, not the release version (`/swagger/v1/swagger.json`) | API/CONTRIBUTING.md "Versioning" |

**API stack** (API-req Technology Stack Document §8; `API/Directory.Packages.props`): .NET 10
(`net10.0`), C# 14; ArturRios.Util 2.1.0, ArturRios.Util.WebApi 5.1.0, ArturRios.Mediator 2.0.0,
ArturRios.Data.Relational.Core 5.0.0, ArturRios.Data.PostgreSql 3.0.2, ArturRios.Messaging
**1.4.0** (props; tech-stack doc says 1.3.0 — §10), ArturRios.Util.Test 5.0.0; EF Core 10.0.12
(Design 10.0.12), EFCore.NamingConventions 10.0.1; FluentValidation 12.1.1; Serilog 4.4.0 /
Serilog.AspNetCore 10.0.0; Google.Apis.Auth 1.77.0; Microsoft.IdentityModel.JsonWebTokens 8.23.0;
Swashbuckle.AspNetCore 10.3.0; Otp.NET 1.4.1; OpenTelemetry 1.19.1 (instrumentation 1.19.0, Prometheus
exporter 1.19.1-beta.1); tests xunit.v3.mtp-off 4.0.2, xunit.runner.visualstudio 4.0.1,
Microsoft.NET.Test.Sdk 18.10.1, coverlet.collector 10.1.0, Moq 4.21.0, Bogus 35.6.5,
Testcontainers.PostgreSql 4.16.0. Functional tests on PostgreSQL 18 (`postgres:18-alpine`)
(API/CHANGELOG.md 1.2.0). Docs: Docsy 0.18.0 (CHANGELOG 1.2.0), Dart Sass 1.105.1 in CI.
Password hashing Argon2id (600 MB / 16 threads defaults) (API-site operations.md).

**UI stack** (UI-req Technology Stack Document §7; `UI/pubspec.yaml`): Flutter 3.47.7, Dart 3.13.5
(`sdk: ^3.13.5`), Material 3; flutter_riverpod ^3.4.3, go_router ^18.0.2, dio ^5.11.1, retrofit
^4.10.0, json_annotation ^4.12.0, flutter_secure_storage ^11.2.0, shared_preferences ^2.5.6,
google_sign_in ^7.2.0 (+ google_sign_in_web ^1.1.3, web ^1.1.1 in pubspec only), qr ^4.0.0,
flutter_markdown_plus ^1.0.12, url_launcher ^6.3.3, path_provider ^2.1.6; swagger_parser ^1.45.0,
build_runner ^2.16.2, json_serializable ^6.14.1, retrofit_generator ^10.2.11; mocktail ^1.0.5;
flutter_lints ^6.0.0. Android: AGP 9.1.1, Kotlin Gradle Plugin 2.4.0, Gradle 9.3.1, compileSdk 37,
JDK 17 (UI/CHANGELOG.md 1.3.0; README).

**License**: on `develop`, both repos "Artur Rios Attribution License" (README "Legal"); OpenAPI
`info.license` now "Artur Rios Attribution License" (`API/docs/openapi/heimdall.json`). Released UI
v1.6.1 (`main`) is still "Proprietary". See §10 item 12.

---

## 9. Deep-link map

### 9.1 API documentation site — https://docs.artur-rios.tech/heimdall-api/

Derived from `API/docs/hugo.toml` (`baseURL = 'https://docs.artur-rios.tech/heimdall-api/'`,
`contentDir = 'content/en'`, mount `requirements` → `content/docs/requirements`, `coverage-report` →
`static/coverage-report`, `openapi` → `static/openapi`) and the content tree; **every URL below
returned HTTP 200 on 2026-10-13** (curl check, before the move to docs.artur-rios.tech: the sites were then on
GitHub Pages). Requirements pages are slugified file names
(`Operations & Infrastructure Document.md` has front-matter `slug: "operations-infrastructure-document"`).
Top nav: Documentation, Requirements, API Explorer, Test Coverage, GitHub.

| URL | Description (front-matter `description` unless noted) |
| --- | --- |
| https://docs.artur-rios.tech/heimdall-api/ | Home: cover, feature blocks (multi-tenant by scope, authentication, identities, getting started, architecture & flows, spec, tests, traceability) |
| https://docs.artur-rios.tech/heimdall-api/docs/ | Everything needed to understand, run, test, and extend the Heimdall API |
| https://docs.artur-rios.tech/heimdall-api/docs/overview/ | Domain vocabulary — scopes, persons, roles, applications, permissions — and the rules that bind them |
| https://docs.artur-rios.tech/heimdall-api/docs/getting-started/ | Prerequisites, configuration, migrations, and running the API locally |
| https://docs.artur-rios.tech/heimdall-api/docs/architecture/ | Four layers, CQRS mediator, auditing decorator, HTTP request pipeline |
| https://docs.artur-rios.tech/heimdall-api/docs/domain-model/ | Entities, relationships, deletion cascade rules — class diagrams |
| https://docs.artur-rios.tech/heimdall-api/docs/api-reference/ | Every endpoint, the role that may call it, and the use case it implements |
| https://docs.artur-rios.tech/heimdall-api/docs/api-explorer/ | Swagger UI over the published OpenAPI document |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/ | Sequence diagrams for the paths worth tracing end to end |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/login/ | UC-11 — password authentication, uniform rejection, branch into 2FA challenge |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/two-factor/ | UC-36 to UC-40 — setup, confirmation, challenge-token round trip, recovery codes |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/google-sign-in/ | UC-24 to UC-29 — enabling per scope, sign-up/sign-in, administering Google Users |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/person-onboarding/ | UC-06, UC-14, UC-15 — creating a person, verification email, replacing a lost link |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/password-recovery/ | UC-12 and UC-13 — an endpoint designed around what it must not reveal |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/scope-permission-claims/ | UC-31 to UC-35 and FR-AU-08 — how a scope permission ends up inside a JWT |
| https://docs.artur-rios.tech/heimdall-api/docs/flows/audit-logging/ | NFR-09 — one decorator, every write, no handler changes |
| https://docs.artur-rios.tech/heimdall-api/docs/operations/ | Migrations, start-up guards, health checks, metrics, logging, rate limiting, data retention, integrations |
| https://docs.artur-rios.tech/heimdall-api/docs/environments-and-deployment/ | The four environments and what each PostgreSQL has to allow (alias `/docs/deploying-with-docker/`) |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/ | The specification index (vision, SRD, use cases, tech stack, data protection, testing, workflow, operations) |
| https://docs.artur-rios.tech/heimdall-api/docs/changelog/ | Notable changes in each release (renders root CHANGELOG.md) |
| https://docs.artur-rios.tech/heimdall-api/docs/contributing/ | Build, tests and coverage, migrations, OpenAPI document, branching and releasing (renders CONTRIBUTING.md) |
| https://docs.artur-rios.tech/heimdall-api/coverage-report/ | ReportGenerator coverage report (generated in CI, not committed) |
| https://docs.artur-rios.tech/heimdall-api/openapi/heimdall.json | The OpenAPI document (raw JSON) |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/vision-document/ | Why Heimdall exists, who it serves, stakeholders, goals, success |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/system-requirements-document/ | FR/NFR, data model, endpoints, authorization matrix, deletion strategy |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/use-case-specification-document/ | Actor-facing use cases with main and numbered alternative flows |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/technology-stack-document/ | Technologies, libraries, pinned versions |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-protection-impact-assessment/ | Risks to data subjects and mitigations — GDPR Art. 35, LGPD Art. 38 |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-retention-schedule-document/ | How long each category of personal data is kept, why, which periods the API enforces |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-protection-document/ | Controllers, bases, recipients, transfers — LGPD Art. 37 / GDPR Art. 30 record |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/privacy-notice/ | What Heimdall does with personal data — LGPD Art. 9, GDPR Art. 13/14 |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-processing-agreement/ | Terms for processing a tenant's users' data — LGPD Art. 39, GDPR Art. 28 |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/incident-response-document/ | Personal data breach definition, declaration, clocks, notification |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/testing-specification-document/ | Unit and functional standards and required coverage per use case |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/threat-model-document/ | Threats by trust boundary and residual risk |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/development-workflow-document/ | Use case from backlog to merged: branch, issue status, testing gate, PR |
| https://docs.artur-rios.tech/heimdall-api/docs/requirements/operations-infrastructure-document/ | Hosting, the four environments, technical foundation, health-check feature |

Useful anchors used by the API README itself: `/docs/operations/#environment-variables-at-a-glance`,
`/docs/operations/#metrics--prometheus`, `/docs/operations/#rate-limiting`,
`/docs/operations/#rotating-the-signing-secret`, `/docs/getting-started/#calling-the-api`,
`/docs/contributing/#releasing`, `/docs/contributing/#migrations`.

### 9.2 Requirements docs on GitHub

Default branch for **both** repos is `develop` (`gh repo view --json defaultBranchRef`). The docs
exist on both `main` and `develop` in both repos (`gh api …/contents/docs/requirements?ref=main`).
Note: the API's Docsy config uses `github_branch = 'main'` and its in-site links use `tree/main`
(API-site docs/_index.md alert). Links below use `develop`.

**heimdall-api** (`https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/…`)
- [Vision Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Vision%20Document.md)
- [System Requirements Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/System%20Requirements%20Document.md)
- [Use Case Specification Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Use%20Case%20Specification%20Document.md)
- [Technology Stack Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Technology%20Stack%20Document.md)
- [Operations & Infrastructure Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Operations%20%26%20Infrastructure%20Document.md)
- [Testing Specification Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Testing%20Specification%20Document.md)
- [Development Workflow Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Development%20Workflow%20Document.md)
- [Threat Model Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Threat%20Model%20Document.md)
- [Data Retention Schedule Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Retention%20Schedule%20Document.md)
- [Data Protection Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Protection%20Document.md)
- [Data Protection Impact Assessment](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Protection%20Impact%20Assessment.md)
- [Privacy Notice](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Privacy%20Notice.md)
- [Data Processing Agreement](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Processing%20Agreement.md)
- [Incident Response Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Incident%20Response%20Document.md)

**heimdall-ui** (`https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/…`; the UI
has **no published docs site** — `homepageUrl` is empty)
- [Vision Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Vision%20Document.md)
- [System Requirements Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/System%20Requirements%20Document.md)
- [Use Case Specification Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Use%20Case%20Specification%20Document.md)
- [Technology Stack Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Technology%20Stack%20Document.md)
- [Testing Specification Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Testing%20Specification%20Document.md)
- [Development Workflow Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Development%20Workflow%20Document.md)
- [Operations & Infrastructure Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Operations%20%26%20Infrastructure%20Document.md)

UI requirement files carry Hugo front matter (`title`, `linkTitle`, `weight`, `description`) like
the API's, so they could be mounted into a Hugo site the same way. Design specs/plans:
`UI/docs/superpowers/specs`, `UI/docs/superpowers/plans` (API has `docs/superpowers/{specs,plans}` too).

Other repo links: CHANGELOGs `https://github.com/artur-rios/heimdall-api/blob/develop/CHANGELOG.md`,
`https://github.com/artur-rios/heimdall-ui/blob/develop/CHANGELOG.md`; CONTRIBUTING likewise;
releases `https://github.com/artur-rios/heimdall-api/releases`, `https://github.com/artur-rios/heimdall-ui/releases`;
UI workflow badges `…/heimdall-ui/actions/workflows/{ci,build,check-api-client}.yml`.

---

## 10. Open uncertainties and contradictions (flagged)

1. **API compliance milestone status.** README "Milestones" says LGPD & GDPR Compliance "🚧 18 / 20"
   and "the three items outstanding are marked `controller-action`", while the same README's
   "Controller actions — all closed" says all three are answered; live GitHub shows 0 open / 39
   closed (milestone still in `open` state). "18/20" vs "three outstanding" is also internally
   inconsistent. Do not quote a fraction; say "all tracked items closed per GitHub" or cite the README.
2. **UI-30 status.** UI/README.md tracker marks UI-30 🚧, but UI/CHANGELOG.md 1.4.0 ships it and
   issue #103 is CLOSED.
3. **UI coverage claim vs API 1.4.0.** UI/README.md and UI-req Vision §1.2 say the UI covers "every
   use case the API exposes". The UI's vendored `api/heimdall.json` (58 operations) lacks
   `/api/auth/register` (UC-47), `/api/scopes/{id}/self-registration`, `/api/scopes/{id}/email-links`
   (API 1.4.0, 61 operations). The UI code also never calls `2fa/challenge/resend` (UC-46),
   `processing-restriction` (UC-44 impose), `erasure-requests` (UC-43) or `erasure-reconciliation`
   (grep of `UI/lib`).
4. **UI password login sends no scope.** `UI/lib/features/auth/data/auth_repository_impl.dart`
   builds `LoginCommand(email: email, password: password)` with no `scopeId`; the API's
   `LoginCommand.ScopeId` is "Required for a `User`" (API `Command/Input/LoginCommand.cs`). The UI scope
   source is read only for Google sign-in (`session_controller.dart` `exchangeGoogleIdToken`). So,
   per code, scope-bound password Users may not be able to sign in through the UI, while UI-req Vision
   §9 says an end user can sign in. Verify before documenting "Users sign in with the UI".
5. **Endpoint count drift.** API/README.md "Run", API-site getting-started.md and api-client/README.md
   say "49 endpoints/operations"; controllers and the committed OpenAPI document have 61.
   API-site api-reference.md omits `register`, `self-registration`, `email-links`,
   `2fa/challenge/resend` and `erasure-reconciliation`.
6. **Challenge-token lifetime.** API-site flows/login.md diagram says "MfaPending, ~5 min"; NFR-17
   (API-req SRD §6) says a fixed **10 minutes**.
7. **ArturRios.Messaging version.** API-req Technology Stack §3/§8 says `1.3.0`;
   `Directory.Packages.props` and API/CHANGELOG.md 1.3.0 say `1.4.0`.
8. **System Admin as scope owner.** API-req Vision §9 says a SystemAdmin "must not belong to any
   scope, either as an owner or as a user" and Vision/SRD §1.3 define owners as ScopeAdmins; API 1.2.0
   (FR-SC-08) allows System Admin owners (CHANGELOG 1.2.0; API-site overview.md).
9. **Application owner.** API-req Vision §9 allows "a User who belongs to it, or a Scope Admin who owns
   it"; FR-AP-03 says owner must be a ScopeAdmin/SystemAdmin owning the scope and "a `User` may never
   own one" (API-site api-reference.md). UI-req SRD FR-AP-03 says "owner drawn from the persons of
   that scope", while UI/CHANGELOG.md 1.1.0 says owner "is chosen from the scope's owners only".
10. **"Person has no scope column."** API-site overview.md says so, but domain-model.md "The scope a
    User belongs to, twice" documents `PERSON.scope_id` as a copy of `SCOPE_USER`; it says "every read
    goes through" `SCOPE_USER`, whereas commit `fa51728` (2026-10-13) notes the email-verification and
    password-reset services read `Person.ScopeId` directly.
11. **Requirements count.** API-site requirements/_index.md says "These fourteen documents" but its
    table lists 13 (Threat Model Document missing); API/README.md's requirements list also omits the
    Threat Model Document (14 files exist; the Threat Model page is live).
12. **License naming history.** API/CHANGELOG.md 1.1.0 and UI/CHANGELOG.md 1.1.0 say the OpenAPI
    licence was corrected to "ArturRios.Heimdall — Proprietary License"; current READMEs and the
    current OpenAPI document say "Artur Rios Attribution License". The UI change is only on
    `develop` (commit #120, unreleased): heimdall-ui `main`/v1.6.1 README "Legal" still reads
    "Proprietary. See LICENSE." and its `LICENSE` is "ArturRios.Heimdall.UI — Proprietary License"
    (`gh api repos/artur-rios/heimdall-ui/contents/README.md?ref=main`). Released UI = proprietary;
    next UI release = attribution licence.
13. **Image tag format.** CONTRIBUTING (both repos) says a release is deployed as image tag
    `1.4.0-<short commit>`; UI/README.md says yggdrasil tags each environment's image
    `<environment>-<version>`; API-site environments-and-deployment.md says image tags "start with
    `<environment>-`". Exact final tag format unclear.
14. **Token issuer/audience defaults.** API/README.md and getting-started list default "Empty" (from
    source); `docker-compose.yml` defaults both to `heimdall` in containers.
15. **Hostnames are placeholders.** All public hosts use `example.com` "standing for the real domain";
    the real domain is not in either repo. Do not publish a production URL.
16. **API local checkout.** The local `heimdall-api` checkout is on `release/1.4.0` and its local
    `main` ref is stale (pre-1.4.0); facts here were taken from the `release/1.4.0` tree, which equals
    remote `develop`/`main` code (`gh api compare main...develop`: develop 0 ahead).
17. **UI test coverage floor.** No numeric UI coverage floor found in UI/CONTRIBUTING.md (only the API
    has the 90% floor); not verified in UI-req Testing Specification beyond its title.
18. **Fortuna.** Mentioned only as an example client system ("Fortuna's API", "fortuna-api") in API
    docs/CHANGELOG; no Fortuna repo or integration contract was read. JWT sharing is inferred only from
    the shared `HEIMDALL_AUTH_TOKEN_SECRET` note.

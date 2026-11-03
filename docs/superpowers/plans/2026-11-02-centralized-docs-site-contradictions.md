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

## Task 4: Application section and the UI parts of Installation

### Between the sources

| # | One source said | Another said | The code says | Kept |
| --- | --- | --- | --- | --- |
| 13 | Architecture, configuration: a calling web application names the scope by writing `sessionStorage.setItem('heimdall.scopeId', ...)` before sending the user to the UI. | heimdall-ui README and Operations document: the caller names it in the URL as `?scope=<PublicId>`, and writing session storage is the legacy path for a caller on the UI's own origin. | `lib/core/entry/entry_link.dart` (`takeEntryLink`) reads the `scope` query parameter, keeps a `PublicId` in session storage and removes the parameter from the address; `lib/core/scope/scope_source.dart` still reads `heimdall.scopeId` for a same-origin caller. | The README. The Application page holds the target scope in full, and the Architecture paragraph now links to it instead of repeating it. |

### Against the code (no second statement)

These were stale facts on pages this task wrote or touched, or statements in the heimdall-ui README that the code corrected.

| # | The page said | The code says | Now |
| --- | --- | --- | --- |
| 14 | Installation, "UI builds from CI": the `build.yml` workflow builds each target on every push to `main` and uploads workflow artifacts (`heimdall-ui-web`, `-linux`, `-windows`, `-android`). | No `build.yml` at `82219b7`: `.github/workflows` holds only `release-windows.yml`. `yggdrasil.yml` has the Jenkins checks and `release.build` (`ci/release-build.sh`: web, Linux, Android) and `release.windows` (dispatches `release-windows.yml`). | "UI release files": the four files a release carries, and who builds each. |
| 15 | Installation: nothing is attached to a GitHub release; releases of both repositories carry no files. | `yggdrasil.yml` lists `files` for the UI release (`dist/*.zip`, `dist/*.tar.gz`, `dist/*.apk`, and the Windows zip). heimdall-api's `yggdrasil.yml` has no `release` step. | An API release has no files; a UI release has four. |
| 16 | Installation, "UI builds from CI": the Android APK of these builds is signed with the debug key. Installation, Build: a release APK is signed with the debug key until a signing configuration is added, which is not part of the project. | `android/app/build.gradle.kts` has a release signing configuration read from `HEIMDALL_UI_KEYSTORE_*` or `android/key.properties`; `ci/release-build.sh` binds the Jenkins keystore credentials. | The release APK is signed with the release key; the debug key is the fallback of a build with no configuration. Detail on the Application page. |
| 17 | heimdall-ui README and Operations document, signing: without the keystore a release still builds, warns, and names the file `heimdall-ui-android-<version>-debug-signed.apk`. | `ci/release-build.sh` exits 1 when `RELEASE_VERSION` is set and `KEYSTORE_BASE64` is empty; only a run with no release version gets the `-debug-signed` file (`heimdall-ui-android-dev-debug-signed.apk`). | The code. |
| 18 | heimdall-ui README, container image: behind yggdrasil's Traefik the proxy replaces the Referrer-Policy header. | `docker/nginx.conf` and the Operations document: yggdrasil's edge from 0.7.4 leaves the header alone (`secure-headers-ui` sets none); an earlier edge or another proxy may replace it. | The code. |

## Task 5: Integrating, Repositories and the rest of the site

### Against the code (no second statement)

These were stale facts on pages this task touched (the Integrating page and the Repositories page); the code corrected them.

| # | The page said | The code says | Now |
| --- | --- | --- | --- |
| 19 | Integrating, "Checking the token": the API signs every token with `HEIMDALL_AUTH_TOKEN_SECRET`, the `fortuna-api` of each VPS environment is given the same value, and a rotation sets `HEIMDALL_AUTH_TOKEN_SECRET_PREVIOUS`; a client system that validates tokens itself must be given the new secret. | `Registration/TokenSecurityRegistrationExtensions.cs` never reads either variable (it only warns that they are set); `Security/TokenSigningKeys.cs` signs ES256 with `HEIMDALL_AUTH_SIGNING_KEY`, `GET /.well-known/jwks.json` publishes the public keys, and `CHANGELOG.md` 4.0.0 says every reader refuses an HS256 token. | The section describes verification against the published key set (ES256 only, key chosen by `kid`, refetch on an unknown `kid`, pin the issuer and the three audiences) and rotation with `HEIMDALL_AUTH_SIGNING_KEY_PREVIOUS`, which needs no change on the consumer. |
| 20 | Integrating, Fortuna: `fortuna-api` validates tokens against `FORTUNA_AUTH_TOKEN_SECRET` (equal to Heimdall's signing secret) and `FORTUNA_AUTH_TOKEN_SECRET_PREVIOUS`. | fortuna-api `FortunaOptions.cs` lists both as retired variables it no longer reads; it requires `FORTUNA_HEIMDALL_JWKS_URL` and fetches the key set when a token names an unknown key, at most once a minute (its Operations & Infrastructure Document, Token validation). | Fortuna verifies with Heimdall's published keys and holds no secret of Heimdall's. |
| 21 | Integrating, Fortuna: `FORTUNA_HEIMDALL_BASE_URL` must be HTTPS. | fortuna-api's Operations & Infrastructure Document (Heimdall exchange) and `Integration/Security/PrivateNetworkConnector.cs`: HTTPS, or plain HTTP to a private address (inside yggdrasil `http://heimdall-api.<environment>:8080/`). | "HTTPS (or plain HTTP to a private address, as inside yggdrasil)". |
| 22 | Integrating, token and claims: Heimdall's API refuses a token only when its identity has since been deleted or restricted. | `Security/ActorLivenessFilter.cs` also refuses a person token whose security stamp (`sst`) is missing or no longer matches (FR-AU-11): after a password reset, an email change, two-factor authentication confirmed or disabled, or recovery codes regenerated. | The sentence names the stamp, and the claims table gains `sst`, which `Security/IdentityUserMapper.cs` writes on every person token. |
| 23 | Repositories: the latest releases are API v1.4.0 and UI v1.6.1, and both releases carry no files; heimdall-docs is published by a Pages workflow from `main`. | `CHANGELOG.md` of each repository, GitHub releases: v4.2.0 and v1.10.0, the latter with four attached files (the API's has none); yggdrasil `catalog.yaml` (the heimdall-docs entry, `production: { trigger: branch, branches: main }`) deploys on every push to `main` from Jenkins; the repositories' home is Forgejo, GitHub a read-only mirror. | The page says so (this repeats item 10 and item 15, which were fixed on the Installation page, for the Repositories page). |
| 24 | Repositories: both repositories track their work on public GitHub project boards and milestones, "the live view of what is done and what is in progress", with links to GitHub's `/milestones` pages. | `gh api repos/artur-rios/heimdall-{api,ui}` returns `has_issues: false`; yggdrasil `docs/cutover.md` 5.11 migrates issues, labels, milestones, releases and pull requests to Forgejo, and 5.12 turns GitHub issues off and sets the description to "Mirror of ... - contribute there". Forgejo's issues and milestones pages answer 303 (sign-in) to an unauthenticated request. I could not establish what the GitHub project boards still show. | Issues and milestones are tracked on Forgejo (named, not linked, since they need a sign-in); the milestone names stay, the "live view" claim and the GitHub board and milestone links are dropped. |

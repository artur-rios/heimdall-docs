---
title: Installation
linkTitle: Installation
weight: 30
description: >
  What you need, and the commands, to get a release, configure and run the Heimdall API, run the Heimdall UI, and point the one at the other.
---

Heimdall is two programs: the Heimdall API (ASP.NET Core on .NET 10, backed by
PostgreSQL) and Heimdall UI (a Flutter application). You run the API first. The
UI is a client of it and has no server of its own. This page covers getting each
one, running each one from source, and the environments Heimdall is deployed to.

The commands are copied from the repositories' own documentation. Where a
detail belongs to operating the API rather than to installing it, such as the
data retention settings, this page links to the
[API documentation]({{< relref "/docs/api" >}}) rather than repeating it.

## Getting a release

Read this section before looking for a download. At the time of writing the
latest releases are API **v4.2.0** and UI **v1.10.0**. Every release of both
repositories carries a tag and generated notes. **An API release has no files
attached.** A UI release has the files listed below. Where a runnable thing
comes from is listed here.

| What | Where it comes from |
| --- | --- |
| API source | Clone [heimdall-api](https://github.com/artur-rios/heimdall-api) and run it as described in [Running the API](#running-the-api). |
| API container image | Built from the repository's `Dockerfile`. Locally you build it yourself with `docker compose` (see [Docker Compose](#option-b-docker-compose)). On the VPS environments, Jenkins builds it per environment. No image is pushed to a registry. The `docker` check Jenkins runs on the repository (`ci/docker.sh`) only checks that the image can be built. |
| UI source | Clone [heimdall-ui](https://github.com/artur-rios/heimdall-ui) and run it as described in [Running the UI](#running-the-ui). |
| UI builds (web, Windows, Linux, Android) | Files attached to a heimdall-ui GitHub release, described in [UI release files](#ui-release-files). |
| UI web container image | Built from the repository's `Dockerfile`. On the VPS environments, Jenkins builds one image per environment. |

### UI release files

A heimdall-ui release carries one file per platform, named with the version (the
tag without its `v`). Two pipelines build them from the release's tag. Jenkins
builds the web, Linux and Android files with `ci/release-build.sh`, as the
`release.build` step of the repository's pipeline file,
[`yggdrasil.yml`](https://github.com/artur-rios/heimdall-ui/blob/main/yggdrasil.yml).
For the Windows file, Jenkins dispatches the `Release Windows` workflow
(`release-windows.yml`) on GitHub Actions against the same tag, waits for it,
and attaches its zip to the release.

| File | Contents | Built by |
| --- | --- | --- |
| `heimdall-ui-web-<version>.zip` | `build/web` | Jenkins |
| `heimdall-ui-linux-x64-<version>.tar.gz` | `build/linux/x64/release/bundle` | Jenkins |
| `heimdall-ui-android-<version>.apk` | the APK from `build/app/outputs/flutter-apk` | Jenkins |
| `heimdall-ui-windows-x64-<version>.zip` | `build/windows/x64/runner/Release` | GitHub Actions |

Three things to know before you use one:

- **They point at `http://localhost:8080`.** The pipelines supply no API base
  URL, on purpose, so that no deployment address appears in a public build log.
  The UI's configuration is fixed when it is built (see
  [Running the UI](#running-the-ui)), so these files are only useful against an
  API that listens on the default address. For any other API, build the UI
  yourself.
- **The Android APK is signed with the release key.** A release without the
  keystore fails instead of publishing a debug-signed file. How the signing is
  configured is under
  [Signing the Android release]({{< relref "/docs/application#signing-the-android-release" >}}).
- **The Windows and Linux files are unsigned.** Nothing in the pipelines signs
  or packages them.

## Running the API

There are two ways to run the API on your own machine: from source with the .NET
SDK ([Option A](#option-a-from-source)), or in a container with Docker Compose
([Option B](#option-b-docker-compose)). Both read the same configuration, described
first. Deploying it to the development, homologation and production environments
is covered in
[Environments and deployment]({{< relref "/docs/installation/environments-and-deployment" >}}).

### Prerequisites

| Requirement | Used for |
| --- | --- |
| .NET 10 SDK | Building and running the API. |
| PostgreSQL | The API's database. The README states no minimum version. The functional tests start their own, `postgres:18-alpine`, through Testcontainers. |
| Python 3 | The migration menu, `scripts/migrations.py`. The other helper scripts under `scripts/` also use it. |
| Docker | Deploying with Compose. The functional tests also start their PostgreSQL container through it. |
| The pinned EF Core CLI | Restored with `dotnet tool restore` (`dotnet-ef` 10.0.13 in `.config/dotnet-tools.json`). |

Building from source, running the test suites and the other contributor tooling
are covered in the API's
[CONTRIBUTING.md](https://github.com/artur-rios/heimdall-api/blob/main/CONTRIBUTING.md).

Clone the repository. The commands that follow run from the repository root.

```bash
git clone https://github.com/artur-rios/heimdall-api.git
cd heimdall-api
```

### Configuration

The API reads its whole configuration from environment variables. When you run
it from source they come from a per-environment file next to a tracked template.
When you run it in a container they come from the env file you give Compose: the
image carries no `Environments/` file.

#### How the environment picks its files

`src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env` is a **tracked
template** listing the variables the API reads. Real values live in
per-environment files, and `ASPNETCORE_ENVIRONMENT` selects two of them, both
resolved next to the built assembly:

| Environment | Variables | App settings |
| --- | --- | --- |
| `Local` (what the launch profiles set) | `Environments/.env.local` | `Settings/appsettings.Local.json` |
| `Development` | `Environments/.env.development` | `Settings/appsettings.Development.json` |
| `Staging` | `Environments/.env.staging` | `Settings/appsettings.Staging.json` |
| `Production` | `Environments/.env.production` | `Settings/appsettings.Production.json` |

Both sets are gitignored: the env files hold credentials, and the app settings
are per machine. `Settings/appsettings.json` is tracked and loaded first, so a
missing environment file costs defaults rather than the whole configuration.

{{% alert title="The fallback hides a missing file" color="warning" %}}
When the file for the current environment does not exist, the loader falls back
to the **default environment, `Local`**, and says so in one line:

```txt
Could not find variables for Development environment. Loading default environment Local instead...
```

That line is easy to miss in a start-up log, and the run then succeeds against
the wrong configuration. That is why the launch profiles name `Local` outright
rather than leaving `Development` to fall back into it.
{{% /alert %}}

#### Required settings

The API will not start without these:

| Variable | Value |
| --- | --- |
| `HEIMDALL_DATA_CONNECTIONSTRING` | A PostgreSQL connection string. |
| `HEIMDALL_DATA_DATABASETYPE` | `PostgreSql`. |
| `HEIMDALL_AUTH_SIGNING_KEY` | The ES256 private key every token is signed with: the one-line base64 of a P-256 PKCS#8 PEM (`openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out signing.pem`, then `base64 -w0 signing.pem`). Start-up throws if it is unset or unusable, naming the variable and never the value. |
| `HEIMDALL_APPLICATION_TOKEN_AUDIENCE` | The `aud` of application tokens (UC-56). Start-up throws if it is unset, or equal to `HEIMDALL_AUTH_TOKEN_AUDIENCE` or to the `.2fa-challenge` or `.subject-rights` audience derived from it: a distinct audience is what stops a consumer taking an application token for a person's. `docker-compose.yml` defaults it to `heimdall-applications` and the `docker/*.env.example` templates preset that value; the Web API's `Environments/.env` holds only a placeholder. |
| `HEIMDALL_MASTER_USER_NAME`, `HEIMDALL_MASTER_USER_EMAIL`, `HEIMDALL_MASTER_USER_PASSWORD` | Credentials for the first System Admin. They are used only while the database holds no System Admin, but the seeder refuses to start without them in that case. |

Generating, publishing and rotating the signing key is covered in
[Signing key](../api/operations/#signing-key).

#### Optional settings

Each of these falls back to a default:

| Variable | Default |
| --- | --- |
| `HEIMDALL_AUTH_TOKEN_ISSUER`, `HEIMDALL_AUTH_TOKEN_AUDIENCE` | Empty. |
| `HEIMDALL_AUTH_TOKEN_EXPIRATION_IN_SECONDS` | `3600` (1 hour). |
| `HEIMDALL_AUTH_SIGNING_KEY_PREVIOUS` | Empty. Set only while [rotating the signing key](../api/operations/#rotating-the-key), to the key being retired, in the same format: its public half stays published and its tokens stay valid, but it never signs. |
| `HEIMDALL_APPLICATION_TOKEN_EXPIRATION_IN_SECONDS` | `600` (10 minutes). |
| `HEIMDALL_AUTH_MAX_CONCURRENT_PASSWORD_HASHES` | `4` (about 2.4 GB of Argon2id working set). |
| `HEIMDALL_INSECURE_TEST_PASSWORD_HASHING` | Unset: the production Argon2id cost (600 MB, 16 lanes). `true` selects the cheapest cost Argon2id accepts, for the test suite only (`tests/default.runsettings` sets it). Start-up refuses it in Production and Staging, and no hash stored under it verifies once it is removed, so never set it in a deployment. |
| `HEIMDALL_EMAIL_VERIFICATION_TOKEN_EXPIRATION_IN_SECONDS` | `86400` (24 hours). |
| `HEIMDALL_PASSWORD_RESET_TOKEN_EXPIRATION_IN_SECONDS` | `3600` (1 hour). |
| `HEIMDALL_ADMIN_EMAIL_COOLDOWN_IN_SECONDS` | `300` (5 minutes): the per-person cooldown on account email, which covers administrator-sent links, anonymous password recovery, and a person's own resends, setup codes and email-change notices (which are also capped at five per day-long window). `0` turns the cooldown off. |
| `HEIMDALL_SCOPE_INVITATION_LIFETIME_IN_SECONDS` | `604800` (7 days): how long a Scope Admin's invitation to co-own a scope can be accepted. 3600 to 2592000; anything else falls back to the default. |
| `HEIMDALL_REGISTRATION_MAX_PENDING_PER_SCOPE` | `1000`: the most live pending self-registrations one scope may hold. A registration beyond it stores and mails nothing, is answered as any other, and is logged with `REGISTRATION_CAP_REACHED`. Any positive integer; anything else falls back to the default. |
| `HEIMDALL_LOG_DIRECTORY` | `logs`. |
| `HEIMDALL_METRICS_PORT` | `9464`, the Prometheus scrape port. `0` switches metrics off (see [Metrics](#metrics)). |
| `HEIMDALL_CORS_ALLOWED_ORIGINS` | Empty, which refuses every cross-origin request. Set it to the front end's origin, comma separated for several (see the CORS note below). |
| `HEIMDALL_TRUSTED_PROXIES` | Empty: `X-Forwarded-For` and `X-Forwarded-Proto` are ignored, and start-up warns. Behind a reverse proxy, set it to the proxy's addresses or CIDR networks (comma separated) so the rate limiter and the request log see the real caller. |
| `HEIMDALL_TRUSTED_CALLER_KEYS` | Empty: no client system may name its users' addresses to the anonymous-auth rate limiter. Comma-separated secrets of at least 32 characters (shorter ones stop start-up); a request with one in `X-Heimdall-Caller-Key` is counted under the address in `X-Heimdall-Client-Address` (see [the API's operations page](../api/operations/#a-client-system-calling-for-its-users--heimdall_trusted_caller_keys)). |

The email and Google settings are described in the next two sections. The data
retention, security monitoring and database TLS settings, with their defaults,
are in the API's
[environment variables at a glance](../api/operations/#environment-variables-at-a-glance)
table.

{{% alert title="CORS blocks a browser UI by default" color="warning" %}}
`HEIMDALL_CORS_ALLOWED_ORIGINS` is empty by default, and an empty value refuses
every cross-origin request. A UI served to a browser from another origin cannot
call the API until that origin is listed. Locally the web UI is served from
`http://localhost:8081`. The local Compose template (`docker/local.env.example`)
already lists that origin. An API run from source does not: its
`Environments/.env.local` is copied from a template in which
`HEIMDALL_CORS_ALLOWED_ORIGINS` is an unfilled placeholder, so set it to
`http://localhost:8081` there (see Option A).
{{% /alert %}}

#### Email delivery

Verification (UC-06) and password reset (UC-12) emails, two-factor codes and the
API's other account emails go out through Mailgun, using
[`ArturRios.Messaging`](https://github.com/artur-rios/dotnet-messaging). Delivery
is enabled only when **both** credentials are present:

| Variable | Value |
| --- | --- |
| `MAILGUN_API_KEY` | Your Mailgun private API key. |
| `MAILGUN_DOMAIN` | The Mailgun sending domain. |
| `MAILGUN_API_VERSION` | Optional; defaults to `v3`. |
| `MAILGUN_FROM` | Optional; the sender, as `Name <address>` or a bare address, for example `Heimdall <no-reply@example.com>`. Unset, mail goes out from a bare `postmaster@<MAILGUN_DOMAIN>`. |

Leave them unset, as local runs and the functional test suite do, and the API
logs each token instead of emailing it, warning once at start-up. That is a
supported mode, not a broken one: it keeps the API runnable without credentials
and keeps the test suite off the network. **In Production it is refused**: an API
running as `Production` without Mailgun will not start, because the fallback
would print tokens and two-factor codes in its log.

Both emails carry a link built from these, with the token appended as a `token`
query parameter. If a link is not configured, the email carries the bare token
instead, which still works: the link is only a convenience wrapper around it.

| Variable | Value |
| --- | --- |
| `HEIMDALL_EMAIL_VERIFICATION_URL` | The front-end page that verifies an email address. |
| `HEIMDALL_PASSWORD_RESET_URL` | The front-end page that sets a new password. |

Each page finishes the job by posting its token back: the verification page to
`POST /api/auth/verify-email` (UC-14), the reset page to
`POST /api/auth/password-reset` (UC-13), along with the new password. Both
endpoints are anonymous, since someone arriving from a link in their mail client
holds no token of any other kind. Heimdall UI serves both pages, at
`/verify-email` and `/password-reset`.

What happens to a token once it is spent, how a lost verification link is
replaced and why a Mailgun failure is never shown to the caller are traced in the
[person onboarding]({{< relref "/docs/api/flows/person-onboarding" >}}) and
[password recovery]({{< relref "/docs/api/flows/password-recovery" >}}) flows. The
Mailgun region, the password recovery queue and the per-scope links that send a
scope's users to a client system's own screens are in the API's
[Email delivery](../api/operations/#email-delivery-mailgun) operations.

#### Google Sign-In

`POST /api/auth/google` (UC-25) signs a Google account up or in against a scope:
the caller sends the ID token they obtained from Google plus the scope's
`PublicId`, and gets back the same kind of bearer token a password login yields.
The first call for a given Google account in a given scope creates the Google
user; every later one authenticates it.

Two things must be true before it works. The scope must have Google Sign-In
switched on through `PUT /api/scopes/{id}/google-signin` (UC-24), which is off by
default, and the API must know which OAuth client the tokens were minted for:

| Variable | Value |
| --- | --- |
| `HEIMDALL_GOOGLE_CLIENT_IDS` | Comma-separated Google OAuth client IDs accepted as an ID token's audience. |

Leave it unset and Google sign-in **refuses every token** with a 401, warning
once at start-up. Unlike the email fallback, this is not a convenience mode:
verification needs an audience to check against (NFR-13), and a verifier with no
configured client could only reject everything or trust everything, so it
rejects. Every other endpoint keeps working, and a scope that never enabled the
feature is unaffected either way.

Signing out, and the endpoints that list and delete a scope's Google users, are
covered in the [Google sign-in flow]({{< relref "/docs/api/flows/google-sign-in" >}}).

### Option A: from source

1. Restore the pinned EF Core CLI, once after cloning.

   ```bash
   dotnet tool restore
   ```

2. Create your local configuration from the tracked template, then fill it in
   with at least the [required settings](#required-settings).

   ```bash
   cp src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env.local
   ```

   Most lines of the tracked template hold a `[[...]]` placeholder, such as
   `HEIMDALL_TRUSTED_CALLER_KEYS=[[trusted-caller-keys]]`, and the loader
   takes each line as written. A placeholder left in is not an empty value: it
   becomes the setting itself. The 23-character trusted-caller placeholder is
   shorter than the 32 characters a caller key needs, so the API refuses to
   start; a left-in `MAILGUN_API_KEY=[[mailgun-api-key]]` counts as a key, and
   the API treats Mailgun as configured once both its key and its domain are
   non-blank. **Replace every `[[...]]` placeholder with a real value, or
   clear the line to take the default.** `HEIMDALL_AUTH_SIGNING_KEY` is the
   exception: it is empty in the template, and the API refuses to start until
   you set it.

   If a browser UI will call this API, also set
   `HEIMDALL_CORS_ALLOWED_ORIGINS=http://localhost:8081`, the origin the web UI
   is served from in [Running the UI](#run) below. The template leaves it as a
   placeholder, and an empty value refuses every cross-origin request.

3. Apply the migrations. The schema is managed with **EF Core migrations,
   applied explicitly**: the API never migrates on start-up and refuses to start
   while migrations are pending, so this comes before the first run, and again
   after every update.

   ```bash
   python scripts/migrations.py
   ```

   The script asks which environment file to load for the connection string,
   then offers list, create and apply. Apply is the one an installation needs.
   It relies on the EF Core CLI restored in step 1. More on migrations is in the
   API's [Migrations](../api/operations/#migrations) operations, and authoring a
   new one is covered in its
   [CONTRIBUTING.md](https://github.com/artur-rios/heimdall-api/blob/main/CONTRIBUTING.md#migrations).

4. Run the API.

   ```bash
   dotnet run --project src/Presentation/ArturRios.Heimdall.WebApi
   ```

The `http` launch profile serves on `http://localhost:5177`, and the `https`
profile adds `https://localhost:7235`.

On the first run against an empty database the seeder creates the three roles
and the master System Admin from the `HEIMDALL_MASTER_USER_*` settings. On later
runs, an existing System Admin means those variables are read but unused.

**Swagger UI** is at `http://localhost:5177/swagger` when the environment is
`Local` or `Development`. It is not served in `Staging` or `Production`. JWT is
wired in: press **Authorize**, paste the token from a login, and call any
endpoint from the browser. It shows each controller's own summary and marks
which endpoints need a token, because it is built from the API's
`SwaggerConfiguration`. That same class produces the document behind the
[API explorer]({{< relref "/docs/api/explorer" >}}), so the two are the same
document: `python scripts/openapi.py` writes byte for byte what a running
instance serves at `/swagger/v1/swagger.json`. Read the API without running it
through the explorer; call it through Swagger UI or `api-client/` (see
[Calling the API](#calling-the-api)).

### Option B: Docker Compose

[`docker-compose.yml`](https://github.com/artur-rios/heimdall-api/blob/main/docker-compose.yml)
runs the API in a container. **PostgreSQL is deliberately not a service in the
file.** The container connects to a PostgreSQL instance that is already
installed on the host, the same instance other services and environments share,
each owning a database of its own. The database and its logins must exist before
you start (see [What the host's PostgreSQL needs](#what-the-hosts-postgresql-needs)).
The local template is written for Docker Desktop on Windows, where
`host.docker.internal` reaches the host's PostgreSQL.

1. Copy the template and fill it in. It documents what each variable expects.
   `DB_USER`, `DB_PASSWORD`, `HEIMDALL_AUTH_SIGNING_KEY` and the three
   `HEIMDALL_MASTER_USER_*` values are empty in the template, and Compose will
   not start until they are set. The real env files are gitignored: they hold
   the database password, the token signing key and the master user's
   credentials.

   ```bash
   cp docker/local.env.example docker/local.env
   ```

2. Build and start the container, from the repository root.

   ```bash
   docker compose --env-file docker/local.env up -d --build
   ```

The API answers at `http://localhost:8080` (the `API_PORT` setting). Compose
reports the container healthy once `/healthcheck` answers. The local environment
runs the API as `Development`, so Swagger UI is at
`http://localhost:8080/swagger`.

Besides the API's own settings, the env file holds ones the API itself never
reads: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_SEARCH_PATH` and `DB_CONNECTION_EXTRA`, from which Compose assembles the
connection string; `API_PORT`, `API_IMAGE` and `API_IMAGE_TAG`;
`HEIMDALL_RUN_MIGRATIONS`, read by the container's entrypoint only;
`HEIMDALL_MIGRATIONS_CONNECTIONSTRING`, read by the entrypoint and by
`scripts/migrations.py`; and `COMPOSE_PROJECT_NAME`.

Pass the env file to every Compose command, not only `up`, because it supplies
the project name:

| Task | Command |
| --- | --- |
| Follow the logs | `docker compose --env-file docker/local.env logs -f api` |
| Rebuild after a code change | `docker compose --env-file docker/local.env up -d --build` |
| Stop it, keeping the log volume | `docker compose --env-file docker/local.env down` |

The step-by-step walkthrough for this local environment, with every command and
the errors each misconfiguration produces, is in
[Environments and deployment]({{< relref "/docs/installation/environments-and-deployment#windows--the-local-environment" >}}).

#### What the container does at start-up

The image carries an **EF Core migrations bundle** built from
`src/Infrastructure/ArturRios.Heimdall.Data/Migrations`. The entrypoint applies
pending migrations and only then starts the API, which is what lets a container
be pointed at an empty database. The API itself still never migrates, and
refuses to start while migrations are pending. Set
`HEIMDALL_RUN_MIGRATIONS=false` (any value other than `true` skips it) to apply
them out of band instead, with `python scripts/migrations.py`, which is required
if an environment ever runs more than one replica.

The bundle migrates with `HEIMDALL_MIGRATIONS_CONNECTIONSTRING` when it is set,
and with the API's own connection string otherwise. Set it to the schema owner's
connection string, and the API can run as a database role that owns nothing,
which is what makes the audit trail's triggers hold against the API's own
credentials (Threat Model TH-18). `scripts/sql` sets the roles up, and the API's
[Database roles](../api/operations/#database-roles--th-18) operations give the
order.

#### Metrics

The container serves Prometheus metrics at `/metrics` on **port 9464**, and only
there: on the API's port 8080 the path is not served. Prometheus is meant to
scrape the container directly over a Docker network it shares with it
(`heimdall-api.<environment>:9464` under yggdrasil), so Compose deliberately does
**not** publish 9464. The endpoint is told apart by the port a connection
arrives on rather than by the `Host` header, which Traefik forwards from the
client and an attacker therefore controls, and publishing the port would undo
that.

`HEIMDALL_METRICS_PORT` moves the endpoint (blank means 9464) or, set to `0`,
switches metrics off. A port other than 9464 must also be added to
`ASPNETCORE_HTTP_PORTS` (the image sets `8080;9464`). What is collected, and the
rules for keeping the port private behind Traefik, are in the API's
[Metrics](../api/operations/#metrics--prometheus) operations.

#### What the host's PostgreSQL needs

The container reaches PostgreSQL over the bridge network, not over the loopback
interface the host's own processes use, so an installation that only listens on
`localhost` is unreachable from it:

- `listen_addresses` must include the address the container connects to. `*`
  binds all interfaces, so pair it with a firewall that does not expose 5432
  publicly, or name the bridge gateway alone.
- `pg_hba.conf` needs a line for the Docker bridge range, for example
  `host heimdall_development heimdall_development_svc 172.16.0.0/12 scram-sha-256`.
- The database and its two roles must exist: an owner the migrations run as, and
  a login the API runs as, which owns nothing. Each service and each environment
  on the shared instance gets its own, so that development and homologation
  cannot reach production's data. `scripts/sql/new-deployment.sql` creates them,
  and each login then needs its password set and one `pg_hba.conf` line, so each
  reaches its own database and no other. A database that belongs to the API's
  own login is moved over with `scripts/sql/separate-owner.sql`.

Docker Desktop on Windows is the exception: it forwards the connection through
its own VM, so the Windows PostgreSQL sees it arrive from `127.0.0.1` and the
stock `pg_hba.conf` already covers it. Neither an extra rule nor a firewall
opening is needed there. A plain Docker engine, as on the VPS, connects over the
bridge for real and needs both.

Check reachability before the first start:

```bash
docker run --rm --add-host host.docker.internal:host-gateway alpine sh -c 'nc -z -w 3 host.docker.internal 5432 && echo reachable || echo unreachable'
```

The exact commands for each host are in
[Environments and deployment]({{< relref "/docs/installation/environments-and-deployment" >}}).

{{% alert title="Do not name the database login heimdall" color="warning" %}}
Compose pins `Search Path=public` in the connection string, and the reason is
worth knowing before anyone changes it. EF names its migrations history table
unqualified, so PostgreSQL resolves it through the search path, whose default,
`"$user", public`, makes the *login's* name a schema lookup. The API's entities
live in a schema called `heimdall`, so a login also named `heimdall` sends the
second run looking for its migration history in that schema, where the first run
wrote none: it concludes nothing was ever applied and fails with
`relation "role" already exists`. The pin makes every run read the table the
first one wrote, whatever the login is called.

The same trap applies when you run from source: `Environments/.env.local` and
`scripts/migrations.py` take the connection string from the env file, not from
Compose. Either keep `Search Path=public` in those connection strings too, or do
not name the login `heimdall`.
{{% /alert %}}

### First calls

Check that the API is up. The liveness check is anonymous and touches no
database. The examples use the source run's port, 5177; a Compose run answers on
8080.

```bash
curl http://localhost:5177/healthcheck
```

Log in as the master System Admin:

```bash
curl -X POST http://localhost:5177/api/auth/login -H "Content-Type: application/json" -d '{"email":"<master-email>","password":"<master-password>"}'
```

The response carries `token`, `expiresAt` and `emailVerified`, the last telling
you whether to prompt the person to confirm their address. Send the token as
`Authorization: Bearer <token>` on every other endpoint. The
[API reference]({{< relref "/docs/api/reference" >}}) says who may call what.

{{% alert title="Two-factor" color="info" %}}
If the person has active two-factor authentication, login answers
`requiresTwoFactor: true` with a short-lived `challengeToken` instead of a full
token. Finish the login at `POST /api/auth/2fa/verify`; see the
[two-factor flow]({{< relref "/docs/api/flows/two-factor" >}}).
{{% /alert %}}

### Calling the API

`api-client/` in the repository holds ready-to-send requests for every operation
in the OpenAPI document, in two formats. Pick whichever your editor already
opens:

| Directory | Format | Opens in |
| --- | --- | --- |
| `api-client/http/` | JetBrains HTTP Client (`.http`) | Rider, IntelliJ IDEA, VS Code with the REST Client extension |
| `api-client/bruno/` | [Bruno](https://www.usebruno.com) collection | The Bruno app, or `bru run` on the command line |

Neither asks you to copy a GUID by hand: a response handler stores the token
that login returns, and each request that creates something stores the new id for
the requests that need it. Point the environment file at your master user's
credentials first, in `http/http-client.env.json` or
`bruno/environments/Local.bru`.

On an empty database four requests have to run in order before anything else
will find its subject: **Login**, then **Create an administrator**, then
**Create a scope**, then **Create a User in a scope**. The collections'
[README](https://github.com/artur-rios/heimdall-api/blob/main/api-client/README.md)
tells the whole story, including how to keep real credentials out of git.

To run the Bruno collection without installing anything:

```bash
npx @usebruno/cli run Auth --env Local
```

## Running the UI

### Prerequisites

Every target needs **Flutter 3.47.7 or newer**, on the stable channel. Each
target adds its own requirements:

| Target | Requirements |
| --- | --- |
| Web | A Chromium-based browser, for `flutter run -d chrome`. |
| Windows | Visual Studio (or Build Tools) with the *Desktop development with C++* workload **and the C++ ATL component**. |
| Linux | `clang`, `cmake`, `ninja-build`, `pkg-config`, `libgtk-3-dev`, `liblzma-dev`, `libstdc++-12-dev` and `libsecret-1-dev`. |
| Android | The Android SDK including `cmdline-tools`, the API 37 platform (`sdkmanager --install "platforms;android-37.0"`), accepted SDK licences (`flutter doctor --android-licenses`) and JDK 17. |

Two of these are easy to miss, and a build fails without them:

- **Windows needs C++ ATL.** `flutter_secure_storage_windows` includes
  `atlstr.h`, and without the ATL component `flutter build windows` fails with
  `Cannot open include file: 'atlstr.h'`. Install it from the Visual Studio
  Installer's *Individual components* tab.
- **Linux needs `libsecret-1-dev`.** It is a dependency of
  `flutter_secure_storage_linux` and is not in Flutter's generic desktop list.
  On Debian or Ubuntu, install the whole list in one command:

  ```bash
  sudo apt-get update && sudo apt-get install -y clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev libstdc++-12-dev libsecret-1-dev
  ```

Check the toolchain, then clone the repository and fetch its packages:

```bash
flutter doctor
```

```bash
git clone https://github.com/artur-rios/heimdall-ui.git
cd heimdall-ui
```

```bash
flutter pub get
```

### Pointing the UI at an API

The UI is configured when it is built, through Dart defines. Nothing is read
from a file at runtime. There are three keys:

| Key | Required | Default |
| --- | --- | --- |
| `HEIMDALL_API_BASE_URL` | In any real deployment | `http://localhost:8080`, the local API |
| `HEIMDALL_GOOGLE_CLIENT_ID` | Only for Google Sign-In | unset, and the Google control is hidden |
| `HEIMDALL_SCOPE_ID` | Only when no calling application supplies a scope | unset |

What each key does is explained under
[Configuration and secure storage]({{< relref "/docs/architecture#configuration-and-secure-storage" >}}),
and how a calling web application names the scope, under
[The target scope]({{< relref "/docs/application#the-target-scope" >}}).
For installation, the key that matters is `HEIMDALL_API_BASE_URL`: it is the
address of the API the build talks to.

Pass the keys on the command line:

```bash
flutter run --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

Or keep them in `config/local.json`, which is git-ignored. Start from the
tracked template, which holds the local values (`http://localhost:8080`, and
empty strings for the other two keys):

```bash
cp config/local.json.example config/local.json
```

```bash
flutter run --dart-define-from-file=config/local.json
```

{{% alert title="These values are public" color="warning" %}}
The keys are compiled into the build. In a web build they are readable by anyone
who loads the page. Never put a secret in one.
{{% /alert %}}

For example, the API run from source (Option A above) listens on port 5177
rather than the UI's default 8080. A UI that calls it needs
`HEIMDALL_API_BASE_URL=http://localhost:5177`, either passed with
`--dart-define` instead of `--dart-define-from-file`, or set in
`config/local.json`. A web UI also needs the API to allow its origin: see the
CORS step in Option A.

### Run

Each command starts the UI from source against the API named in
`config/local.json`, which holds `http://localhost:8080` unless you change it.
To run against an API from source on port 5177, edit `HEIMDALL_API_BASE_URL` in
that file, or replace `--dart-define-from-file=config/local.json` in a command
with `--dart-define=HEIMDALL_API_BASE_URL=http://localhost:5177`. Swapping in a
single `--dart-define` drops any other key you set in `config/local.json`, such
as the scope id or the Google client id, so pass those too.

```bash
flutter run -d chrome --web-port 8081 --dart-define-from-file=config/local.json
```

```bash
flutter run -d windows --dart-define-from-file=config/local.json
```

```bash
flutter run -d linux --dart-define-from-file=config/local.json
```

```bash
flutter run -d android --dart-define-from-file=config/local.json
```

`--web-port 8081` gives the web page the origin `http://localhost:8081`, which
the local Compose template allows through CORS. An API run from source allows it
only if you set `HEIMDALL_CORS_ALLOWED_ORIGINS=http://localhost:8081` in its
`.env.local`. Stop a local heimdall-ui container first, because it serves on the
same port.

### Build

Each command makes a release build configured for a real API. Replace the URL
with your own API's address.

```bash
flutter build web --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

```bash
flutter build windows --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

```bash
flutter build linux --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

```bash
flutter build apk --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

| Target | Output |
| --- | --- |
| Web | `build/web`, a static bundle. The host must fall back to `index.html` for deep links, and the API must allow the origin the bundle is served from. |
| Windows | `build/windows/x64/runner/Release` |
| Linux | `build/linux/x64/release/bundle` |
| Android | `build/app/outputs/flutter-apk` |

Android can also build an App Bundle, written to `build/app/outputs/bundle/release`:

```bash
flutter build appbundle --release --dart-define=HEIMDALL_API_BASE_URL=https://heimdall.example.com
```

To serve the web bundle under a sub-path, add `--base-href=/heimdall/` to the
web build command.

Without a signing configuration, a release APK is signed with the debug key, so
it is suitable for testing and not for distribution. The configuration is
described under
[Signing the Android release]({{< relref "/docs/application#signing-the-android-release" >}}).
Signing and packaging the Windows and Linux builds (MSIX, AppImage, deb) is not
part of the repository.

### Web container image

The repository's `Dockerfile` builds the web target into an image that serves it
with nginx on port 8080, as a non-root user, with a deep-link fallback and a
`/healthz` probe. It expects TLS to be terminated in front of it. The build
arguments are `HEIMDALL_API_BASE_URL` (required, and the build fails without it),
`HEIMDALL_GOOGLE_CLIENT_ID`, `HEIMDALL_SCOPE_ID`, and the pair
`FLUTTER_VERSION` and `FLUTTER_SHA256`, which override the pinned SDK and must be
passed together.

```bash
docker build -t heimdall-ui:web \
  --build-arg HEIMDALL_API_BASE_URL=https://heimdall-api.example.com \
  --build-arg HEIMDALL_GOOGLE_CLIENT_ID=1234567890-abc.apps.googleusercontent.com \
  --build-arg HEIMDALL_SCOPE_ID=00000000-0000-0000-0000-000000000001 \
  .
docker run --rm -p 8080:8080 heimdall-ui:web
```

The example publishes the container's port 8080 on the host's port 8080, which
is also where the local Compose deployment of the API listens. If both run on
one machine, publish the UI on another host port, for example `-p 8081:8080`.
The values are baked in at build time, so each environment needs its own image
build.

## Environments

Heimdall runs in four environments: `local`, `development`, `homologation` and
`production`. The API and the UI share the same four. Local is the developer's
own machine, deployed by hand as described above. The other three share one
Ubuntu VPS and are deployed by Jenkins, through
[yggdrasil](https://github.com/artur-rios/yggdrasil). The API runs as
`Development` locally and in development, as `Staging` in homologation and as
`Production` in production. Development and homologation are on demand and run
only while somebody uses them. No public host names are given here, because the
repositories use `example.com` as a stand-in for the real domain.
[Environments and deployment]({{< relref "/docs/installation/environments-and-deployment" >}})
has the full table for the API, and the walkthroughs for each host.

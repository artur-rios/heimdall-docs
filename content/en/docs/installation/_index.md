---
title: Installation
linkTitle: Installation
weight: 30
description: >
  What you need, and the commands, to get a release, run the Heimdall API, run the Heimdall UI, and point the one at the other.
---

Heimdall is two programs: the Heimdall API (ASP.NET Core on .NET 10, backed by
PostgreSQL) and Heimdall UI (a Flutter application). You run the API first. The
UI is a client of it and has no server of its own. This page covers getting each
one, running each one from source, and the environments Heimdall is deployed to.

The commands are copied from the repositories' own documentation. Where a
detail changes often, such as the full list of API settings, this page links to
the source rather than repeating it.

## Getting a release

Read this section before looking for a download, because **nothing is attached
to a GitHub release**. At the time of writing the latest releases are API
**v1.4.0** and UI **v1.6.1**. Every release of both repositories carries a tag
and generated notes, and no files. Where a runnable thing does come from is
listed below.

| What | Where it comes from |
| --- | --- |
| API source | Clone [heimdall-api](https://github.com/artur-rios/heimdall-api) and run it as described in [Running the API](#running-the-api). |
| API container image | Built from the repository's `Dockerfile`. Locally you build it yourself with `docker compose` (see [Docker Compose](#option-b-docker-compose)). On the VPS environments, Jenkins builds it per environment. No image is pushed to a registry. The `docker` job in the `tests.yml` workflow only checks that the image can be built. |
| UI source | Clone [heimdall-ui](https://github.com/artur-rios/heimdall-ui) and run it as described in [Running the UI](#running-the-ui). |
| UI builds (web, Windows, Linux, Android) | Workflow artifacts of the [Build workflow](https://github.com/artur-rios/heimdall-ui/actions/workflows/build.yml), described below. |
| UI web container image | Built from the repository's `Dockerfile`. On the VPS environments, Jenkins builds one image per environment. |

### UI builds from CI

The `build.yml` workflow runs on every push to `main` and can also be started by
hand (`workflow_dispatch`). It builds each target and uploads the result as a
workflow artifact:

| Artifact name | Contents |
| --- | --- |
| `heimdall-ui-web` | `build/web` |
| `heimdall-ui-linux` | `build/linux/x64/release/bundle` |
| `heimdall-ui-windows` | `build/windows/x64/runner/Release` |
| `heimdall-ui-android` | the APK from `build/app/outputs/flutter-apk` |

Three things to know before you use one:

- **They are workflow artifacts, not release files.** GitHub keeps
  workflow artifacts only for its own retention period, and downloading them
  needs a GitHub sign-in, so there is no permanent download link.
- **They point at `http://localhost:8080`.** The workflow supplies no API base
  URL, on purpose, so that no deployment address appears in a public build log.
  The UI's configuration is fixed when it is built (see
  [Running the UI](#running-the-ui)), so these artifacts are only useful against
  an API that listens on the default address. For any other API, build the UI
  yourself.
- **The Android APK is signed with the debug key.** The workflow says it is
  suitable for testing, never for release. The Windows and Linux builds are
  unsigned, and no target updates itself.

## Running the API

### Prerequisites

| Requirement | Used for |
| --- | --- |
| .NET 10 SDK | Building and running the API. |
| PostgreSQL | The API's database. The README states no minimum version. The functional tests start their own, `postgres:18-alpine`, through Testcontainers. |
| Python 3 | The migration menu, `scripts/migrations.py`. The other helper scripts under `scripts/` also use it. |
| Docker | Deploying with Compose. The functional tests also start their PostgreSQL container through it. |
| The pinned EF Core CLI | Restored with `dotnet tool restore` (`dotnet-ef` 10.0.12 in `.config/dotnet-tools.json`). |

Clone the repository. The documentation site's theme is a git submodule, so the
command below fetches it too. The API itself does not need it.

```bash
git clone --recurse-submodules https://github.com/artur-rios/heimdall-api.git
```

### Configuration

The API reads its whole configuration from environment variables. When you run
it from source they come from a per-environment file next to a tracked template.
When you run it in a container they come from the env file you give Compose.

These are required, and the API will not start without them:

| Variable | What it is |
| --- | --- |
| `HEIMDALL_DATA_CONNECTIONSTRING` | A PostgreSQL connection string. |
| `HEIMDALL_DATA_DATABASETYPE` | `PostgreSql`. |
| `HEIMDALL_AUTH_TOKEN_SECRET` | The JWT signing secret. |
| `HEIMDALL_MASTER_USER_NAME`, `HEIMDALL_MASTER_USER_EMAIL`, `HEIMDALL_MASTER_USER_PASSWORD` | Credentials for the first System Admin. They are used only while the database holds no System Admin, but the seeder refuses to start without them in that case. |

Everything else is optional and has a default. By name, the optional settings
cover:

- **Tokens**: `HEIMDALL_AUTH_TOKEN_ISSUER`, `HEIMDALL_AUTH_TOKEN_AUDIENCE`,
  `HEIMDALL_AUTH_TOKEN_EXPIRATION_IN_SECONDS`, `HEIMDALL_AUTH_TOKEN_SECRET_PREVIOUS`
  (only while rotating the secret), `HEIMDALL_AUTH_MAX_CONCURRENT_PASSWORD_HASHES`,
  `HEIMDALL_EMAIL_VERIFICATION_TOKEN_EXPIRATION_IN_SECONDS` and
  `HEIMDALL_PASSWORD_RESET_TOKEN_EXPIRATION_IN_SECONDS`.
- **Network**: `HEIMDALL_CORS_ALLOWED_ORIGINS`, `HEIMDALL_TRUSTED_PROXIES`,
  `HEIMDALL_TRUSTED_CALLER_KEYS` and `HEIMDALL_METRICS_PORT`.
- **Integrations**: `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_API_VERSION`,
  `MAILGUN_FROM`, `HEIMDALL_EMAIL_VERIFICATION_URL`, `HEIMDALL_PASSWORD_RESET_URL`
  and `HEIMDALL_GOOGLE_CLIENT_IDS`.
- **Data protection and monitoring**: `HEIMDALL_DATA_REQUIRE_TLS`, the
  `HEIMDALL_RETENTION_*` settings, the `HEIMDALL_MONITORING_*` settings and
  `HEIMDALL_LOG_DIRECTORY`.
- **Compose only**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
  `DB_SEARCH_PATH`, `DB_CONNECTION_EXTRA`, `API_PORT`, `API_IMAGE`,
  `API_IMAGE_TAG`, `HEIMDALL_RUN_MIGRATIONS` and `COMPOSE_PROJECT_NAME`.

The defaults and the meaning of every setting are in the API's
[Getting started](https://artur-rios.github.io/heimdall-api/docs/getting-started/)
page and in its
[environment variables at a glance](https://artur-rios.github.io/heimdall-api/docs/operations/#environment-variables-at-a-glance)
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

### Option A: from source

1. Restore the pinned EF Core CLI, once after cloning.

   ```bash
   dotnet tool restore
   ```

2. Create your local configuration from the tracked template, then fill it in
   with at least the required settings above.

   ```bash
   cp src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env src/Presentation/ArturRios.Heimdall.WebApi/Environments/.env.local
   ```

   If a browser UI will call this API, also set
   `HEIMDALL_CORS_ALLOWED_ORIGINS=http://localhost:8081`, the origin the web UI
   is served from in the Run section below. The template leaves it as a
   placeholder, and an empty value refuses every cross-origin request.

   The `ASPNETCORE_ENVIRONMENT` value selects which file is read:
   `Environments/.env.<local|development|staging|production>`, with matching
   `Settings/appsettings.<Environment>.json`. The launch profiles set it to
   `Local`. If the file for the current environment is missing, the API falls
   back to `Local` and only logs a line saying so, which is easy to miss.

3. Apply the migrations. The API never migrates on start-up and refuses to start
   while migrations are pending, so this comes before the first run, and again
   after every update.

   ```bash
   python scripts/migrations.py
   ```

   The script asks which environment file to load for the connection string,
   then offers list, create and apply. Apply is the one an installation needs.

4. Run the API.

   ```bash
   dotnet run --project src/Presentation/ArturRios.Heimdall.WebApi
   ```

The `http` launch profile serves on `http://localhost:5177`, and the `https`
profile adds `https://localhost:7235`. Swagger UI is at
`http://localhost:5177/swagger` when the environment is `Local` or
`Development`. It is not served in `Staging` or `Production`.

On the first run against an empty database the seeder creates the three roles
and the master System Admin from the `HEIMDALL_MASTER_USER_*` settings. Check
that the API is up, then log in as that user:

```bash
curl http://localhost:5177/healthcheck
```

The first calls on an empty database are, in order, login, create an
administrator, create a scope, and create a User in a scope. The API's
[Getting started](https://artur-rios.github.io/heimdall-api/docs/getting-started/)
page walks through them.

### Option B: Docker Compose

[`docker-compose.yml`](https://github.com/artur-rios/heimdall-api/blob/develop/docker-compose.yml)
runs the API in a container. **PostgreSQL is deliberately not a service in the
file.** The container connects to a PostgreSQL instance that is already
installed on the host, and the database and its login must exist before you
start. The local template is written for Docker Desktop on Windows, where
`host.docker.internal` reaches the host's PostgreSQL.

1. Copy the template and fill it in. `DB_USER`, `DB_PASSWORD`,
   `HEIMDALL_AUTH_TOKEN_SECRET` and the three `HEIMDALL_MASTER_USER_*` values are
   empty in the template, and Compose will not start until they are set.

   ```bash
   cp docker/local.env.example docker/local.env
   ```

2. Build and start the container, from the repository root.

   ```bash
   docker compose --env-file docker/local.env up -d --build
   ```

The API answers at `http://localhost:8080` (the `API_PORT` setting). On start the
container applies pending EF Core migrations before it starts the API, so it can
be pointed at an empty database. Set `HEIMDALL_RUN_MIGRATIONS=false` to apply
them yourself with `python scripts/migrations.py` instead, which is required if
an environment ever runs more than one replica. Compose reports the container
healthy once `/healthcheck` answers.

Pass the env file to every Compose command, not only `up`, because it supplies
the project name:

| Task | Command |
| --- | --- |
| Follow the logs | `docker compose --env-file docker/local.env logs -f api` |
| Rebuild after a code change | `docker compose --env-file docker/local.env up -d --build` |
| Stop it, keeping the log volume | `docker compose --env-file docker/local.env down` |

{{% alert title="Do not name the database login heimdall" color="warning" %}}
The API's entities live in a schema called `heimdall`. A PostgreSQL login with
the same name makes the second run look for its migration history in that
schema and fail with `relation "role" already exists`. Compose pins
`Search Path=public` to avoid it, and the same trap applies when you run from
source. The API's
[Environments and deployment](https://artur-rios.github.io/heimdall-api/docs/environments-and-deployment/)
page walks through creating the database and login and what each host's
PostgreSQL has to allow.
{{% /alert %}}

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

What each key does, and how a calling web application names the scope with
`sessionStorage`, is explained under
[Configuration and secure storage]({{< relref "/docs/architecture#configuration-and-secure-storage" >}}).
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
with `--dart-define=HEIMDALL_API_BASE_URL=http://localhost:5177`.

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

A release APK is signed with the debug key until a signing configuration is
added to the project, so it is suitable for testing and not for distribution.
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
Ubuntu VPS and are deployed by Jenkins, with the API running as
`Development`, `Staging` and `Production` respectively. Development and
homologation are on demand and run only while somebody uses them. No public host
names are given here, because the repositories use `example.com` as a stand-in
for the real domain. The API's
[Environments and deployment](https://artur-rios.github.io/heimdall-api/docs/environments-and-deployment/)
page has the full table, and the walkthroughs for each host.

---
title: Application documentation
linkTitle: Application
weight: 55
description: >
  Heimdall UI in detail: what it is and where it runs, the scope it acts in, its environments, signing and releasing it, its web container image, and the specification.
---

Heimdall UI is the Flutter application that drives the Heimdall API. It covers every use case the API
exposes: signing in, answering a second factor, recovering a password, verifying an address, managing
your own profile, and administering scopes, persons, applications, scope permissions and Google users.
This section is its operator's documentation: the parts of running and shipping it that the
[Installation]({{< relref "/docs/installation" >}}) page does not already teach, and the specification
it is built from.

One codebase ships to four platforms: **web** (a static bundle that runs in any modern browser),
**Windows** and **Linux** (desktop applications) and **Android** (an APK or an App Bundle). What each
person sees follows their role, and that is a usability decision, not a security one; see
[Role-based UI]({{< relref "/docs/architecture#role-based-ui" >}}). For how the application is built,
see [UI architecture]({{< relref "/docs/architecture#ui-architecture" >}}).

## Where each topic lives

| To | Go to |
| --- | --- |
| Install the prerequisites for a platform, clone the repository and fetch its packages | [Running the UI]({{< relref "/docs/installation#running-the-ui" >}}) |
| Set `HEIMDALL_API_BASE_URL`, `HEIMDALL_GOOGLE_CLIENT_ID` and `HEIMDALL_SCOPE_ID` | [Pointing the UI at an API]({{< relref "/docs/installation#pointing-the-ui-at-an-api" >}}) |
| Run it from source, and build it for each platform | [Run]({{< relref "/docs/installation#run" >}}) and [Build]({{< relref "/docs/installation#build" >}}) |
| Get a released build | [UI release files]({{< relref "/docs/installation#ui-release-files" >}}) |
| Build and run the web container image | [Web container image]({{< relref "/docs/installation#web-container-image" >}}) |
| Know which scope the UI acts in | [The target scope](#the-target-scope), below |
| Know where each environment lives | [Environments](#environments), below |
| Sign the Android release | [Signing the Android release](#signing-the-android-release), below |
| Know what the web image's server sends | [The web image's server](#the-web-images-server), below |
| See which use cases are done | [Use case status](use-case-status/) |
| Read the specification | [Requirements](requirements/) |

## Configuration the build needs

The keys are build-time Dart defines and nothing is read from a file at runtime. One rule is not on
the Installation page: **a release build of the Windows, Linux or Android app refuses to start unless
`HEIMDALL_API_BASE_URL` is an `https://` address.** Only `http://localhost` and `http://127.0.0.1` are
let through in the clear. The app then shows a screen saying why, and writes the same line to the
log. Debug and profile builds and the web build are not held to it.

## The target scope

Heimdall UI is opened by the applications that use Heimdall's services, and the scope being entered is
theirs to name. No screen here asks for it, and there is no endpoint an anonymous caller could list
scopes from. On the **web**, the calling application names the scope's `PublicId` in the URL it sends
the user to, as the `scope` query parameter, on any route:

```text
https://heimdall.example.com/login?scope=<scope-public-id>
```

At start-up the UI checks that the value is a GUID, copies it into its own **session storage**
(`heimdall.scopeId`) and removes it from the address bar. A value that is not a GUID is ignored and
removed. Session storage rather than a cookie: it is scoped to the tab, so two tabs can act in two
scopes; it is never attached to a request, so the scope cannot become a header the API did not ask
for; and it dies with the tab, so a scope does not outlive the visit on a shared machine. It is read
on every use, so opening the UI again with another `scope` changes it.

{{% alert title="Host the calling application on its own origin" color="warning" %}}
Never use the UI's origin (the same scheme, host and port). Script on that origin can read everything
the UI keeps in the browser, the session token included, so a flaw in a co-hosted caller would become
a flaw in Heimdall UI.
{{% /alert %}}

A caller that already shares the UI's origin may still write the value itself, as earlier versions
required: `sessionStorage.setItem('heimdall.scopeId', '<scope-public-id>')`. It keeps working and is
held to the same rule, since a value that is not a GUID is ignored, but moving to the URL and to an
origin of the caller's own is the way forward.

`HEIMDALL_SCOPE_ID` is the fallback for a build with no such caller: the Windows, Linux and Android
platforms, or a web build opened directly. When neither supplies a scope, the request is made without
one and the API decides what that means.

## Environments

The UI runs in the same four environments as the API, which
[Environments and deployment]({{< relref "/docs/installation/environments-and-deployment" >}}) describes
for the API. The UI has no env file of its own: a deployed build's values are build arguments, kept
with the API's in [yggdrasil](https://github.com/artur-rios/yggdrasil)'s env files on the VPS
(`/etc/yggdrasil/<environment>/heimdall-ui.env`). `example.com` stands for the real domain.

| Environment | Where | Deployed by | UI at | `HEIMDALL_API_BASE_URL` |
| --- | --- | --- | --- | --- |
| `local` | The developer's Windows machine, Docker Desktop | By hand: `flutter run`, or yggdrasil's `scripts/deploy.sh local heimdall-ui ...` | `http://localhost:8081` | `http://localhost:8080`, the local API (`config/local.json.example`) |
| `development` | The VPS, on demand | Jenkins, on every push to `develop` | `https://heimdall-dev.example.com` | `https://heimdall-dev.example.com`, the same origin |
| `homologation` | The VPS, on demand | Jenkins, on every push of a `release/x.y.z` branch | `https://heimdall-hml.example.com` | `https://heimdall-hml.example.com`, the same origin |
| `production` | The VPS, always on | Jenkins, on a green `release/x.y.z` to `main` pull request | `https://heimdall.example.com` | `https://heimdall.example.com`, the same origin |

On the VPS the API base URL is the UI's own origin: Traefik routes `/api/` on the UI's host to that
environment's API, so the browser makes no cross-origin request and the API needs no CORS entry.
Locally the UI and the API are two origins, so the API's `docker/local.env.example` lists
`http://localhost:8081` in `HEIMDALL_CORS_ALLOWED_ORIGINS`; that is why the
[run commands]({{< relref "/docs/installation#run" >}}) pass `--web-port 8081`. Development and
homologation run only while they are used: `scripts/ygg.sh env start <environment>` on the VPS turns
one on.

## Signing the Android release

A release APK is signed with a keystore held outside the repository. The Gradle build reads these
environment variables, or `android/key.properties` (git-ignored, for a local build) with the keys in
the last column:

| Variable | Meaning | `key.properties` key |
| --- | --- | --- |
| `HEIMDALL_UI_KEYSTORE_PATH` | The keystore file, absolute or relative to `android/` | `storeFile` |
| `HEIMDALL_UI_KEYSTORE_PASSWORD` | The keystore password | `storePassword` |
| `HEIMDALL_UI_KEY_ALIAS` | The key's alias | `keyAlias` |
| `HEIMDALL_UI_KEY_PASSWORD` | The key's password; defaults to the keystore password | `keyPassword` |

With none of them set, the release build signs with the **debug key** and prints a warning, which a
plain `flutter build apk --release` shows too: that APK is for testing only and must not be
distributed. Setting some of the first three but not all, or naming a keystore that does not exist,
fails the release build. A debug build is not affected.

A release is built by Jenkins (`ci/release-build.sh`), which reads the same values from the Jenkins
credentials `heimdall-ui-android-keystore` (the keystore, base64-encoded),
`heimdall-ui-android-keystore-password`, `heimdall-ui-android-key-alias` and
`heimdall-ui-android-key-password`, bound to that build alone. A release without the keystore fails
rather than publish a debug-signed APK; the script run by hand, with no release version, still builds,
warns, and names the file `heimdall-ui-android-dev-debug-signed.apk`. The files a release carries, and
who builds each, are under
[UI release files]({{< relref "/docs/installation#ui-release-files" >}}).

## The web image's server

The web container image is built and run as
[Installation]({{< relref "/docs/installation#web-container-image" >}}) describes. A pinned Flutter
SDK (3.47.7, the version CI uses) compiles `build/web`, and `nginxinc/nginx-unprivileged` serves it;
the server configuration is
[`docker/nginx.conf`](https://github.com/artur-rios/heimdall-ui/blob/main/docker/nginx.conf). It
expects TLS to be terminated in front of it.

It sends an enforced Content-Security-Policy whose `connect-src` names the API's origin, taken from
`HEIMDALL_API_BASE_URL` at build time, and `no-referrer` on the password reset and verification
pages, where a token is in the address. Behind yggdrasil's Traefik edge from 0.7.4 on, that header
reaches the browser as nginx sent it; behind a proxy that replaces it, the token's removal from the
address as the page starts is the protection. The headers, and how to check them, are in the
Operations document's
[Security headers](requirements/documents/operations--infrastructure-document/#51-security-headers).

Because the build arguments become `--dart-define` values, they are compiled into the JavaScript
bundle and readable by anyone who loads the page. They are public: never pass a secret as one. Each
environment needs its own image, so yggdrasil builds one per environment and tags it
`<environment>-<version>`.

## Specification

The [requirements](requirements/) are the seven documents Heimdall UI is built from: the vision, the
system requirements and screen inventory, the use cases (`UI-01` to `UI-39`) with their flows traced
to the API use cases they consume, the technology stack, testing, the development workflow, and
operations. [Use case status](use-case-status/) tracks which of them are done.

## Changes and contributing

The notable changes in each release are in the
[CHANGELOG](https://github.com/artur-rios/heimdall-ui/blob/main/CHANGELOG.md). The project structure,
regenerating the API client, running the tests, the branching model and the release process are in
[CONTRIBUTING](https://github.com/artur-rios/heimdall-ui/blob/main/CONTRIBUTING.md). Both live in the
repository and are not rendered on this site.

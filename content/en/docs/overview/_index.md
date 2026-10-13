---
title: Overview
linkTitle: Overview
weight: 10
description: >
  What Heimdall is, what it is not, and the concepts the rest of the documentation assumes.
---

## What Heimdall is

Heimdall is a centralized identity-management system for many client systems at
once. Each client system delegates its people and its sign-in to Heimdall and
gets an isolated slice of the data, called a scope.

It has two parts.

- **Heimdall API** is a centralized identity management API built with ASP.NET
  Core (.NET 10). It manages persons and applications, authenticates them, and
  decides what they may do. It also handles password recovery, email
  verification and Google Sign-In.
- **Heimdall UI** is the Flutter front-end for that API. One codebase ships to
  the web, Windows, Linux and Android. It covers the end-user flows (sign in,
  second factor, password recovery, your own profile) and the administration of
  scopes, persons, applications, scope permissions and Google users.

On top of that, the API supports optional two-factor authentication, logical and
hard deletion with defined cascades, the data-subject rights of LGPD and GDPR
(export, erasure and restriction), and, for scopes that open it,
self-registration.

## What it is not

- **Not an authorization layer in the UI.** What each person sees follows their
  role, but that is a usability decision. The API is the only authority on what
  anyone may do, and the UI holds no identity data of its own.
- **Not available on iOS or macOS.** Those platforms are out of scope for the UI.
- **Not a token revocation service.** Tokens are stateless signed JWTs, and
  Google sign-out revokes nothing.
- **Not a way to sign administrators in with Google.** Google Sign-In never
  creates or authenticates a Scope Admin or a System Admin.
- **Not a two-factor option for Google users.** Two-factor authentication is
  available to persons only.
- **Not a replacement for a WAF or an API gateway.** The API's rate limiter is a
  per-instance, defence-in-depth throttle.
- **Not self-updating.** No desktop or Android target updates itself.
  Distribution and update are the operator's responsibility.
- **Not shipped signed or packaged.** Windows and Linux builds are unsigned by
  default, and signing and packaging them (MSIX, AppImage, deb) is a deployment
  decision outside the repository. Android release builds need a signing
  configuration; without one they are signed with the debug key, which is fine
  for testing and not for distribution.

## Concepts

### Scopes

A scope is the tenant boundary of one client system. It groups that system's
owners, users, applications, Google users and permissions, and keeps them apart
from every other scope. Google Sign-In is a per-scope setting that is off by
default. Since API 1.4.0 a scope can also open self-registration, which is off by
default, and can point its verification and password-reset emails at the client
system's own screens. The full rules are in the API's
[overview](https://artur-rios.github.io/heimdall-api/docs/overview/).

### Roles

There are three roles, held in a closed set. A **System Admin** belongs to no
scope and governs the whole system; since API 1.2.0 a System Admin may also own a
scope. A **Scope Admin** owns one or more scopes, manages the users and
applications in them, and can add co-owners. A Scope Admin who owns no live scope
cannot sign in. A **User** belongs to exactly one scope and can sign in, view
their own profile, recover a password and verify an email address. The
authorization matrix is in the API's
[system requirements](https://artur-rios.github.io/heimdall-api/docs/requirements/system-requirements-document/).

### Persons

A person is a human identity: a name, an email, a password hash, a role and a
deletion status. A User's scope is the one scope they belong to, a Scope Admin's
scopes are the ones they own, and a System Admin has none. The same email can
exist as a User in several scopes, while administrators' emails are unique across
the system. Outside the database a person is addressed by a public GUID, never by
the internal id. How a sign-in finds the right person is described in the API's
[login flow](https://artur-rios.github.io/heimdall-api/docs/flows/login/).

### Applications

An application is a non-human identity, usually another system. It lives in
exactly one scope and is owned by one Scope Admin or System Admin who owns that
scope. A User may never own an application. The endpoints that manage them are
listed in the API's
[API reference](https://artur-rios.github.io/heimdall-api/docs/api-reference/).

### Scope permissions

A scope can define named permissions, each with an optional description and an
`IncludeAsJwtClaim` flag. When a token is issued, the names of the flagged
permissions are added to its `scopePermissions` claim, so a client system can
read them without a further call. The claim is a snapshot, and a change is picked
up at the next sign-in. A User gets the permissions of their scope, a Scope Admin
gets those of all the scopes they own, and a System Admin gets none. See the
API's
[scope permission claims](https://artur-rios.github.io/heimdall-api/docs/flows/scope-permission-claims/)
flow.

### Google users

A Google user is an identity authenticated by Google instead of a password. It
always has the User role, belongs to exactly one scope, and is stored apart from
persons. A scope must switch Google Sign-In on before its people can use it.
Google users do not get two-factor authentication. The sequence is in the API's
[Google sign-in flow](https://artur-rios.github.io/heimdall-api/docs/flows/google-sign-in/).

### Two-factor authentication

Two-factor authentication is opt-in for each person, in all three roles. The
second factor is an authenticator app, an email code, or both, backed by ten
single-use recovery codes. Once it is active, sign-in returns a short-lived
challenge token instead of the access token, and that challenge token can be
redeemed only once. The setup, the challenge and the recovery codes are traced in
the API's
[two-factor flow](https://artur-rios.github.io/heimdall-api/docs/flows/two-factor/).

### Deletion strategies

Deletion is either logical or hard. A logical delete sets a flag and keeps the
row; deleting a scope this way cascades to its users, Google users and
applications, but not to its owners or its permissions. A hard delete removes the
row along with the records that depend on it, and only a System Admin can do it.
A scope must always keep at least one owner, so removing a scope's last owner, or
hard-deleting the person who is its last owner, is rejected. The cascade
rules are in the API's
[domain model](https://artur-rios.github.io/heimdall-api/docs/domain-model/).

## Where to go next

- To see how the pieces fit together, read [Architecture]({{< relref "/docs/architecture" >}}).
- To run the API and the UI, read [Installation]({{< relref "/docs/installation" >}}).
- To use the interface, read the [User guide]({{< relref "/docs/user-guide" >}}).
- To connect a system to Heimdall, read [Integrating a client system]({{< relref "/docs/integrating" >}}).
- For the endpoints, the generated reference and the specification, read [API documentation]({{< relref "/docs/api" >}}).
- For the source, the releases and the specification documents, read [Repositories]({{< relref "/docs/repositories" >}}).

The [Heimdall API documentation](https://artur-rios.github.io/heimdall-api/docs/)
holds the detailed rules behind everything summarised here.

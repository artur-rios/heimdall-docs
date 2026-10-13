---
title: User guide
linkTitle: User guide
weight: 40
description: >
  How to use Heimdall UI, task by task: signing in, managing your account, and administering scopes, persons, applications, permissions and Google users.
---

This guide describes what you can do in Heimdall UI and how to do it. It follows
the UI's own Use Case Specification Document: each task is one use case, named
`UI-01` to `UI-30`, with the steps of its main flow and the notable things that
can go differently. Every use case appears once, on the page for its group.

You need a running Heimdall API and UI first. The
[Installation]({{< relref "/docs/installation" >}}) page covers both. The terms
used here (scope, role, person, application, permission) are explained in the
[Overview]({{< relref "/docs/overview" >}}).

## The pages of this guide

| Page | What it covers | Use cases | Who uses it |
| --- | --- | --- | --- |
| [Signing in]({{< relref "/docs/user-guide/signing-in" >}}) | Sign in with a password, the second factor, Google Sign-In, and how the UI decides which screens you may open. | UI-01, UI-02, UI-06, UI-07 | Everyone |
| [Password and email]({{< relref "/docs/user-guide/password-and-email" >}}) | Recover a forgotten password, set a new one, and verify an email address. | UI-03, UI-04, UI-05 | Anyone, signed in or not |
| [Restricted sessions]({{< relref "/docs/user-guide/restricted-sessions" >}}) | The single screen a person gets when processing of their account is restricted. | UI-30 | Restricted subjects |
| [Your account]({{< relref "/docs/user-guide/your-account" >}}) | Your own profile and your two-factor settings. | UI-08, UI-09 | System Admin, Scope Admin, User |
| [Scopes]({{< relref "/docs/user-guide/scopes" >}}) | Browse, create, update and delete scopes, manage owners, switch Google Sign-In. | UI-10 to UI-15 | System Admin, Scope Admin |
| [Persons]({{< relref "/docs/user-guide/persons" >}}) | The people of a scope. | UI-16 to UI-19 | System Admin, Scope Admin |
| [Applications]({{< relref "/docs/user-guide/applications" >}}) | The applications of a scope. | UI-20 to UI-23 | System Admin, Scope Admin |
| [Scope permissions]({{< relref "/docs/user-guide/permissions" >}}) | The named permissions of a scope and whether they go into tokens. | UI-24 to UI-27 | System Admin, Scope Admin |
| [Google users]({{< relref "/docs/user-guide/google-users" >}}) | The identities created when someone signs in to a scope with Google. | UI-28, UI-29 | System Admin, Scope Admin |

## Who can reach what

What the UI shows follows the role in your session. There are three roles, and a
fourth case, a restricted session, that is described on its own page. The
[Architecture]({{< relref "/docs/architecture#role-based-ui" >}}) page has a
diagram of the same rules.

| Pages | System Admin | Scope Admin | User | Not signed in | Restricted session |
| --- | --- | --- | --- | --- | --- |
| Signing in; password and email | Not offered once signed in | Not offered once signed in | Not offered once signed in | Full | Not offered |
| Second-factor challenge | Full | Full | Full | Only with a held challenge | Not offered |
| Restricted sessions | Not offered | Not offered | Not offered | Not offered | Full |
| Your account (profile, two-factor) | Full | Full | Full | Not offered | Not offered |
| Scopes: listing, detail, owners, Google Sign-In switch | All scopes | Owned scopes only | Not offered | Not offered | Not offered |
| Scopes: create, delete, permanent delete | Full | Not offered | Not offered | Not offered | Not offered |
| Scopes: change name and description | Full | Read-only | Not offered | Not offered | Not offered |
| Persons, applications, permissions: list, create, update, delete | Full | Owned scopes only | Not offered | Not offered | Not offered |
| Google users: list, detail, delete | Full | Owned scopes only | Not offered | Not offered | Not offered |
| Any permanent delete (person, application, permission, Google user) | Full | Not offered | Not offered | Not offered | Not offered |

"Not offered" means the screen or control is hidden, or a screen says it is not
available for your role. "Owned scopes only" means the screen works for the
scopes you own; asking for another scope shows a "Not available for your role"
panel.

### Screens outside the use cases

Three screens belong to no numbered use case but are part of what you see.

- **Home** is the first screen after you sign in. Everyone sees their own
  account there: the address and whether it is verified, whether two-factor
  authentication is on, and the role. A System Admin or Scope Admin also sees an
  overview of the scopes they administer, such as how many there are and how many
  Users, applications, permissions and Google users they hold, summed over the
  first ten scopes.
- **Privacy notice** at `/privacy` shows the Heimdall API's own Privacy Notice.
  Anyone can open it, signed in or not, and a restricted session may open it too.
- **Health** shows whether the API is reachable. A System Admin gets the full
  report, a Scope Admin gets a read-only view, and a User does not see it.

## Things that work the same everywhere

- **Errors come from the API.** When a request is refused, the UI shows the
  messages the API returned, next to the field they name or in a banner when no
  field is named. The API is the only authority; the UI hides what your role
  cannot use, but it never grants anything.
- **Records are read-only until you press Edit.** On the profile and on the
  scope, person, application and permission detail screens, the fields open for
  editing only after **Edit**. Editing offers **Cancel**, which puts back what
  the API holds, and **Save changes**, which stays disabled until something
  differs. If you may not change a record, **Edit** is not offered.
- **Deleting asks first.** Every deletion opens a confirmation that names the
  record. A permanent deletion also asks you to type the record's name before the
  confirm button works; for a person or a Google user you type the email address.
- **Listings** show cards on a narrow window and a table on a wide one. They have
  a search field, an **Include deleted** switch and paging. Changing the search or
  the switch returns to the first page. An empty listing tells "nothing yet" apart
  from "nothing matches your search".
- **Leaving unsaved work asks first.** A form you have changed asks before you
  discard it.

## What the UI does not cover

The UI covers the use cases listed above. A few API capabilities have no UI and
are done through the API. The first three rows below are missing from the copy
of the API specification the UI is built from (API 1.4.0 has 61 operations, the
copy has 58). For the other rows the UI has no screen that calls them.

| Capability | API use case | Endpoint |
| --- | --- | --- |
| Register a password User | UC-47, Register a Password User | `POST /api/auth/register` |
| Open or close self-registration for a scope | Scope setting that belongs to UC-47 | `PUT /api/scopes/{id}/self-registration` |
| Set the base links of a scope's verification and password-reset emails | Scope setting, `email-links` | `PUT /api/scopes/{id}/email-links` |
| List outstanding erasure requests | UC-43, List Outstanding Erasure Requests | `GET /api/auth/erasure-requests` |
| Restrict processing of your own identity | UC-44, Restrict Processing of Own Identity | `POST /api/auth/processing-restriction` |
| Resend the second-factor email code | UC-46, Resend Second-Factor Email Code | `POST /api/auth/2fa/challenge/resend` |
| Re-apply erasure after a database restore | `erasure-reconciliation` | `POST /api/auth/erasure-reconciliation` |

Use the API's [API reference](https://artur-rios.github.io/heimdall-api/docs/api-reference/)
for who may call each one and what it expects, or the
[API Explorer](https://artur-rios.github.io/heimdall-api/docs/api-explorer/) to
try them. Note that the restricted-session screen can lift a restriction
(UC-45), download your data (UC-41) and request erasure (UC-42), but cannot
impose a restriction in the first place; that is UC-44, above.

The source of this guide is the UI's
[Use Case Specification Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Use%20Case%20Specification%20Document.md)
and its
[System Requirements Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/System%20Requirements%20Document.md).
Where the screens differ from the specification, this guide describes the
screens.

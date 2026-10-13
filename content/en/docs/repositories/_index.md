---
title: Repositories
linkTitle: Repositories
weight: 70
description: >
  The repositories behind Heimdall, their releases, every specification document each code repository holds, and where to follow the work.
---

Heimdall lives in two code repositories, the API and the UI, and this
documentation site has a repository of its own. Both code repositories keep
their specification documents in `docs/requirements/`, and both track their work
on GitHub project boards and milestones.

## The repositories

| Repository | What it holds | Default branch | Latest release |
| --- | --- | --- | --- |
| [heimdall-api](https://github.com/artur-rios/heimdall-api) | The identity-management API, built with ASP.NET Core on .NET 10, with its documentation site, specification documents and tests. | `develop` | [v1.4.0](https://github.com/artur-rios/heimdall-api/releases/tag/v1.4.0) |
| [heimdall-ui](https://github.com/artur-rios/heimdall-ui) | The Flutter application for the web, Windows, Linux and Android that drives the API, with its specification documents. | `develop` | [v1.6.1](https://github.com/artur-rios/heimdall-ui/releases/tag/v1.6.1) |
| [heimdall-docs](https://github.com/artur-rios/heimdall-docs) | This site: documentation only, no software and no package. | `main`, the branch its Pages workflow publishes from | None |

Both releases are marked **Latest** on GitHub. Each repository's
[releases page](https://github.com/artur-rios/heimdall-api/releases)
([UI](https://github.com/artur-rios/heimdall-ui/releases)) lists every version,
and each repository's `CHANGELOG.md` is the curated record of what changed:
[API](https://github.com/artur-rios/heimdall-api/blob/develop/CHANGELOG.md),
[UI](https://github.com/artur-rios/heimdall-ui/blob/develop/CHANGELOG.md).

{{% alert title="GitHub releases carry no files" color="warning" %}}
The releases of both code repositories have no attached files. How to get a
runnable API or UI from them is in
[Getting a release]({{< relref "/docs/installation#getting-a-release" >}}).
{{% /alert %}}

The documentation of each code repository is on its default branch,
`develop`. The links below use `develop`, and the same documents also exist on
`main`.

## heimdall-api

The API's specification is 14 documents in
[`docs/requirements/`](https://github.com/artur-rios/heimdall-api/tree/develop/docs/requirements).
All of them are also published on the
[API site](https://artur-rios.github.io/heimdall-api/docs/requirements/), and the
[API documentation]({{< relref "/docs/api" >}}) page maps that site.

### Product and engineering documents

| Document | What it is |
| --- | --- |
| [Vision Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Vision%20Document.md) | Why Heimdall exists, who it serves, its stakeholders, goals and what success looks like. |
| [System Requirements Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/System%20Requirements%20Document.md) | The functional and non-functional requirements, the data model, the endpoints, the authorization matrix and the deletion strategy. |
| [Use Case Specification Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Use%20Case%20Specification%20Document.md) | The actor-facing use cases, each with its main flow and numbered alternative flows. |
| [Technology Stack Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Technology%20Stack%20Document.md) | The technologies, libraries and pinned versions the project is built on. |
| [Operations & Infrastructure Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Operations%20%26%20Infrastructure%20Document.md) | Hosting, the four environments, the technical foundation and the health-check feature. |
| [Testing Specification Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Testing%20Specification%20Document.md) | How each use case is tested: the unit and functional standards and the required coverage. |
| [Development Workflow Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Development%20Workflow%20Document.md) | How a use case goes from backlog to merged: branch, issue status, testing gate and pull request. |

### Data-protection and security documents

| Document | What it is |
| --- | --- |
| [Data Protection Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Protection%20Document.md) | Who controls what, on what basis, shared with whom and across which borders: the record LGPD Art. 37 and GDPR Art. 30 require. |
| [Data Protection Impact Assessment](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Protection%20Impact%20Assessment.md) | The risks the system creates for the people in it, and what is done about them: GDPR Art. 35, LGPD Art. 38. |
| [Data Retention Schedule Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Retention%20Schedule%20Document.md) | How long each category of personal data is kept, why, and which periods the API enforces itself. |
| [Privacy Notice](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Privacy%20Notice.md) | What Heimdall does with personal data, told to the people it belongs to: LGPD Art. 9, GDPR Art. 13 and 14. |
| [Data Processing Agreement](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Data%20Processing%20Agreement.md) | The terms on which Heimdall processes a tenant's users' data: LGPD Art. 39, GDPR Art. 28. |
| [Incident Response Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Incident%20Response%20Document.md) | What counts as a personal data breach, who declares one, the clocks that start, and who has to be told. |
| [Threat Model Document](https://github.com/artur-rios/heimdall-api/blob/develop/docs/requirements/Threat%20Model%20Document.md) | What the security controls defend against, organised by trust boundary, and what remains after them. |

## heimdall-ui

The UI's specification is seven documents in
[`docs/requirements/`](https://github.com/artur-rios/heimdall-ui/tree/develop/docs/requirements).
The UI has no documentation site of its own, so these pages on GitHub are the
source. The [User guide]({{< relref "/docs/user-guide" >}}) on this site draws on
them.

| Document | What it is |
| --- | --- |
| [Vision Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Vision%20Document.md) | Why Heimdall UI exists, who it serves, its stakeholders, goals and what success looks like. |
| [System Requirements Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/System%20Requirements%20Document.md) | The functional and non-functional requirements, the screen inventory and the authorization matrix. |
| [Use Case Specification Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Use%20Case%20Specification%20Document.md) | The UI use cases, their flows, and how each one traces back to the API use cases it consumes. |
| [Technology Stack Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Technology%20Stack%20Document.md) | The technologies, libraries and pinned versions Heimdall UI is built on. |
| [Operations & Infrastructure Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Operations%20%26%20Infrastructure%20Document.md) | How Heimdall UI is configured, built, packaged and released for each of its four targets and four environments. |
| [Testing Specification Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Testing%20Specification%20Document.md) | How each use case is tested: the levels, the naming convention, the structure, and what coverage means here. |
| [Development Workflow Document](https://github.com/artur-rios/heimdall-ui/blob/develop/docs/requirements/Development%20Workflow%20Document.md) | How a use case goes from backlog to merged: branch, issue status, testing gate and pull request. |

## Project boards and milestones

Work on both repositories is tracked on public GitHub project boards, which are
the live view of what is done and what is in progress.

| Repository | Project board | Milestones |
| --- | --- | --- |
| heimdall-api | [Project board](https://github.com/users/artur-rios/projects/7) | [Milestones](https://github.com/artur-rios/heimdall-api/milestones): MVP, Google Sign-In, and LGPD & GDPR Compliance |
| heimdall-ui | [Heimdall UI Delivery](https://github.com/users/artur-rios/projects/11) | [Milestones](https://github.com/artur-rios/heimdall-ui/milestones): Platform & Infrastructure, Authentication & Session, Profile & Security, Scope Management, Person Management, Application Management, Scope Permission Management, and Google Users |

The board and the milestone pages show the current state. The READMEs of the
repositories carry their own status tables, but GitHub is the source of truth, so
this site does not repeat progress counts that would go stale.

Each issue moves from its first status through In Progress and Testing to Done,
and each use case ships on its own branch, issue and pull request, as the Development
Workflow Documents describe.

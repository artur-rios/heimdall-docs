---
title: Repositories
linkTitle: Repositories
weight: 70
description: >
  The repositories behind Heimdall, where they live, their releases, every specification document each code repository holds, and where to follow the work.
---

Heimdall lives in two code repositories, the API and the UI, and this
documentation site has a repository of its own. Both code repositories keep
their specification documents in `docs/requirements/`, and both track their work
as issues and milestones on Forgejo.

## Where the code lives

The home of each repository is Forgejo, at
`git.techcraftsmen.net/artur-rios/<repository>`. The GitHub repository of the
same name is a read-only mirror of it, and the links on this site point at the
mirror because it is public. To contribute, e-mail
[arturdev@duck.com](mailto:arturdev@duck.com); each code repository's CONTRIBUTING
file says how to build, test and branch.

Jenkins runs the checks, the releases and the deploys of every repository from the
`yggdrasil.yml` file at its root (see
[yggdrasil](https://github.com/artur-rios/yggdrasil)), not from GitHub workflows (the UI's Windows build is the one exception: Jenkins dispatches it). A release
of the API or the UI is a `release/x.y.z` branch merged into `main` by a pull request that Jenkins
merges, and it is published on Forgejo and mirrored to GitHub. This site is deployed by Jenkins
on every push to `main`.

## The repositories

| Repository | What it holds | Default branch | Latest release |
| --- | --- | --- | --- |
| [heimdall-api](https://github.com/artur-rios/heimdall-api) | The identity-management API, built with ASP.NET Core on .NET 10, with its specification documents and tests. | `develop` | [v4.2.0](https://github.com/artur-rios/heimdall-api/releases/tag/v4.2.0) |
| [heimdall-ui](https://github.com/artur-rios/heimdall-ui) | The Flutter application for the web, Windows, Linux and Android that drives the API, with its specification documents. | `develop` | [v1.10.0](https://github.com/artur-rios/heimdall-ui/releases/tag/v1.10.0) |
| [heimdall-docs](https://github.com/artur-rios/heimdall-docs) | This site: documentation only, no software and no package. | `main`, the branch Jenkins deploys on every push | None |

Both releases are marked **Latest** on GitHub. Each repository's
[releases page](https://github.com/artur-rios/heimdall-api/releases)
([UI](https://github.com/artur-rios/heimdall-ui/releases)) lists every version.
Each code repository also keeps two files that this site links rather than renders:

| Repository | What changed | How to contribute |
| --- | --- | --- |
| heimdall-api | [CHANGELOG](https://github.com/artur-rios/heimdall-api/blob/main/CHANGELOG.md) | [CONTRIBUTING](https://github.com/artur-rios/heimdall-api/blob/main/CONTRIBUTING.md) |
| heimdall-ui | [CHANGELOG](https://github.com/artur-rios/heimdall-ui/blob/main/CHANGELOG.md) | [CONTRIBUTING](https://github.com/artur-rios/heimdall-ui/blob/main/CONTRIBUTING.md) |

{{% alert title="Only the UI's releases carry files" color="warning" %}}
A heimdall-api release has no attached files, so a runnable API comes from the
source or from its container image. A heimdall-ui release attaches four: the web
bundle, the Linux and Windows builds and the Android APK. How to get either is in
[Getting a release]({{< relref "/docs/installation#getting-a-release" >}}) and
[UI release files]({{< relref "/docs/installation#ui-release-files" >}}).
{{% /alert %}}

The documentation of each code repository is on its default branch, `develop`,
and the same documents also exist on `main`. The links to the repository folders
below use `main`, which receives each release: a release is cut from `develop` as
`release/x.y.z` and merged into `main`.

## The specification on this site

The requirements documents are shown here, not only linked: on each release of a
code repository, the yggdrasil `sync` feature copies its `docs/requirements/` folder into this
site, as the [API requirements]({{< relref "/docs/api/requirements" >}}) and the
[application requirements]({{< relref "/docs/application/requirements" >}}). It also copies
the API's OpenAPI document and its test coverage report. The copies are never edited
here: change the Markdown in the repository and the next release updates this site.

## heimdall-api

The API's specification is 14 documents in
[`docs/requirements/`](https://github.com/artur-rios/heimdall-api/tree/main/docs/requirements).
They are shown on this site, as the [API requirements]({{< relref "/docs/api/requirements" >}}),
copied from the repository on each release. The
[API documentation]({{< relref "/docs/api" >}}) section covers the rest of the API.

### Product and engineering documents

| Document | What it is |
| --- | --- |
| [Vision Document](../api/requirements/documents/vision-document/) | Why Heimdall exists, who it serves, its stakeholders, goals and what success looks like. |
| [System Requirements Document](../api/requirements/documents/system-requirements-document/) | The functional and non-functional requirements, the data model, the endpoints, the authorization matrix and the deletion strategy. |
| [Use Case Specification Document](../api/requirements/documents/use-case-specification-document/) | The actor-facing use cases, each with its main flow and numbered alternative flows. |
| [Technology Stack Document](../api/requirements/documents/technology-stack-document/) | The technologies, libraries and pinned versions the project is built on. |
| [Operations & Infrastructure Document](../api/requirements/documents/operations-infrastructure-document/) | Hosting, the four environments, the technical foundation and the health-check feature. |
| [Testing Specification Document](../api/requirements/documents/testing-specification-document/) | How each use case is tested: the unit and functional standards and the required coverage. |
| [Development Workflow Document](../api/requirements/documents/development-workflow-document/) | How a use case goes from backlog to merged: branch, issue status, testing gate and pull request. |

### Data-protection and security documents

| Document | What it is |
| --- | --- |
| [Data Protection Document](../api/requirements/documents/data-protection-document/) | Who controls what, on what basis, shared with whom and across which borders: the record LGPD Art. 37 and GDPR Art. 30 require. |
| [Data Protection Impact Assessment](../api/requirements/documents/data-protection-impact-assessment/) | The risks the system creates for the people in it, and what is done about them: GDPR Art. 35, LGPD Art. 38. |
| [Data Retention Schedule Document](../api/requirements/documents/data-retention-schedule-document/) | How long each category of personal data is kept, why, and which periods the API enforces itself. |
| [Privacy Notice](../api/requirements/documents/privacy-notice/) | What Heimdall does with personal data, told to the people it belongs to: LGPD Art. 9, GDPR Art. 13 and 14. |
| [Data Processing Agreement](../api/requirements/documents/data-processing-agreement/) | The terms on which Heimdall processes a tenant's users' data: LGPD Art. 39, GDPR Art. 28. |
| [Incident Response Document](../api/requirements/documents/incident-response-document/) | What counts as a personal data breach, who declares one, the clocks that start, and who has to be told. |
| [Threat Model Document](../api/requirements/documents/threat-model-document/) | What the security controls defend against, organised by trust boundary, and what remains after them. |

## heimdall-ui

The UI's specification is seven documents in
[`docs/requirements/`](https://github.com/artur-rios/heimdall-ui/tree/main/docs/requirements).
They are shown on this site, as the [application requirements]({{< relref "/docs/application/requirements" >}}),
copied from the repository on each release. The
[Application documentation]({{< relref "/docs/application" >}}) section covers the rest of the UI, and
the [User guide]({{< relref "/docs/user-guide" >}}) draws on these documents.

| Document | What it is |
| --- | --- |
| [Vision Document](../application/requirements/documents/vision-document/) | Why Heimdall UI exists, who it serves, its stakeholders, goals and what success looks like. |
| [System Requirements Document](../application/requirements/documents/system-requirements-document/) | The functional and non-functional requirements, the screen inventory and the authorization matrix. |
| [Use Case Specification Document](../application/requirements/documents/use-case-specification-document/) | The UI use cases, their flows, and how each one traces back to the API use cases it consumes. |
| [Technology Stack Document](../application/requirements/documents/technology-stack-document/) | The technologies, libraries and pinned versions Heimdall UI is built on. |
| [Operations & Infrastructure Document](../application/requirements/documents/operations--infrastructure-document/) | How Heimdall UI is configured, built, packaged and released for each of its four targets and four environments. |
| [Testing Specification Document](../application/requirements/documents/testing-specification-document/) | How each use case is tested: the levels, the naming convention, the structure, and what coverage means here. |
| [Development Workflow Document](../application/requirements/documents/development-workflow-document/) | How a use case goes from backlog to merged: branch, issue status, testing gate and pull request. |

## Issues and milestones

Work on both repositories is tracked as issues and milestones on Forgejo, at
`git.techcraftsmen.net/artur-rios/<repository>`; the pages need a sign-in, so this
site does not link them. The issues, labels, milestones, releases and pull requests
were migrated there from GitHub, and the GitHub repositories have issues turned
off. The milestones are:

| Repository | Milestones |
| --- | --- |
| heimdall-api | MVP, Google Sign-In, and LGPD & GDPR Compliance |
| heimdall-ui | Platform & Infrastructure, Authentication & Session, Profile & Security, Scope Management, Person Management, Application Management, Scope Permission Management, and Google Users |

The READMEs of the repositories carry their own status tables. This site does
not track use case status: the pages
[API use case status]({{< relref "/docs/api/use-case-status" >}}) and
[application use case status]({{< relref "/docs/application/use-case-status" >}})
say where to find it. It does not repeat progress counts that would go stale.

Each issue moves from Todo through In Progress and Testing to Done,
and each use case ships on its own branch, issue and pull request, as the Development
Workflow Documents describe.

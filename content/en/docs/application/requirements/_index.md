---
title: 'Requirements'
linkTitle: 'Requirements'
weight: 90
description: 'The specification: vision, system requirements, use cases, technology stack, testing, workflow, and operations.'
---

These seven documents are the **specification** for Heimdall UI. The rest of the application
documentation describes how to run and ship it; these say what must be true.

They are also the working documents of the project, not a retrospective write-up: a screen is built by
picking a use case, following its main and alternative flows, and citing the requirement identifiers in
the code.

| Document | What it settles |
| --- | --- |
| [Vision Document](documents/vision-document/) | Why Heimdall UI exists, who it serves, its stakeholders, goals, and what success looks like. |
| [System Requirements Document](documents/system-requirements-document/) | The functional and non-functional requirements, the screen inventory, and the authorization matrix. |
| [Use Case Specification Document](documents/use-case-specification-document/) | The Heimdall UI use cases (`UI-01` to `UI-39`), their flows, and how each one traces back to the API use cases it consumes. |
| [Technology Stack Document](documents/technology-stack-document/) | The technologies, libraries, and pinned versions Heimdall UI is built on, and how the API client is generated. |
| [Testing Specification Document](documents/testing-specification-document/) | How each use case is tested: the levels, the naming convention, the structure, and what coverage means here. |
| [Development Workflow Document](documents/development-workflow-document/) | How a use case goes from backlog to merged: branch, issue status, testing gate, pull request. |
| [Operations & Infrastructure Document](documents/operations--infrastructure-document/) | How Heimdall UI is configured, built, packaged, and released for each of its four targets and four environments. |

{{% alert title="Copies of the repository's documents" color="info" %}}
The pages in this section are copies of the files under
[`docs/requirements/`](https://github.com/artur-rios/heimdall-ui/tree/main/docs/requirements) in the
heimdall-ui repository. A CI job copies them into this site, so they are never edited here: change the
Markdown in the repository and the next sync updates this site.
{{% /alert %}}

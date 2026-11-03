---
title: 'Requirements'
linkTitle: 'Requirements'
weight: 90
cascade:
  # The documents/ pages are copies that a sync takes from heimdall-api; their edit and view links
  # must open the source file there, not the copy in this repository.
  - target:
      path: '/docs/api/requirements/documents/**'
    github_repo: 'https://github.com/artur-rios/heimdall-api'
    github_branch: 'main'
    github_subdir: 'docs/requirements'
    path_base_for_github_subdir:
      from: '^.*content.en.docs.api.requirements.documents.'
      to: ''
description: 'The specification: vision, system requirements, use cases, technology stack, data protection, testing, workflow, and operations.'
---

These fourteen documents are the **specification** for the Heimdall API. The rest of the API
documentation describes what was built; these say what must be true.

They are also the working documents of the project, not a retrospective write-up: a feature is
implemented by picking a use case, following its main and alternative flows, and citing the
requirement identifiers in the code.

| Document | What it settles |
| --- | --- |
| [Vision Document](documents/vision-document/) | Why the system exists, who it serves, and what success looks like. |
| [System Requirements Document](documents/system-requirements-document/) | The functional (`FR-…`) and non-functional (`NFR-…`) requirements, the data model, the endpoints, the authorization matrix, and the deletion strategy. |
| [Use Case Specification Document](documents/use-case-specification-document/) | Every use case (`UC-…`) with its main flow and numbered alternative flows (`AF-11a`, `AF-11b`, …). |
| [Technology Stack Document](documents/technology-stack-document/) | The technologies, libraries, and **pinned versions**. The single source of truth for versions. |
| [Data Retention Schedule Document](documents/data-retention-schedule-document/) | How long each category of personal data is kept and why — the record NFR-19 requires, and the source of truth the retention passes are configured against. |
| [Data Protection Document](documents/data-protection-document/) | Who controls what, on what basis, shared with whom, and across which borders — the record LGPD Art. 37 and GDPR Art. 30 require. |
| [Data Protection Impact Assessment](documents/data-protection-impact-assessment/) | The risks this system creates for the people in it, rated for them rather than for the system. |
| [Privacy Notice](documents/privacy-notice/) | What Heimdall does with personal data, told to the people it belongs to. Versioned, and the Encarregado's published contact. |
| [Data Processing Agreement](documents/data-processing-agreement/) | The terms on which Heimdall processes a tenant's users' data, and the sub-processor list. |
| [Incident Response Document](documents/incident-response-document/) | What counts as a personal data breach, who declares one, the clocks that start, and who has to be told. |
| [Testing Specification Document](documents/testing-specification-document/) | What to test for each use case, the unit and functional standards, and the required coverage. |
| [Development Workflow Document](documents/development-workflow-document/) | How a use case goes from backlog to merged — branch, issue status, testing gate, pull request. |
| [Operations & Infrastructure Document](documents/operations-infrastructure-document/) | The technical foundation and the health-check feature. |
| [Threat Model Document](documents/threat-model-document/) | The threats by trust boundary, and the residual risk. |

## Identifier conventions

| Prefix | Meaning | Example |
| --- | --- | --- |
| `FR-XX-nn` | Functional requirement, grouped by capability | `FR-AU-04` — the claims an auth token carries |
| `NFR-nn` | Non-functional requirement | `NFR-15` — internal ids never reach a caller |
| `UC-nn` | Use case | `UC-11` — Login |
| `AF-nna` | Alternative flow within a use case | `AF-11g` — the person has active 2FA |

The capability groups are `SC` (scope), `PE` (person), `RO` (role), `AU` (authentication), `PR`
(password recovery), `EV` (email verification), `AP` (application), `GO` (Google Sign-In), `SP`
(scope permission), `2F` (two-factor), `HC` (health check).

{{% alert title="Copies of the repository's documents" color="info" %}}
The pages in this section are copies of the files under
[`docs/requirements/`](https://github.com/artur-rios/heimdall-api/tree/main/docs/requirements) in the
heimdall-api repository. A CI job copies them into this site, so they are never edited here: change the
Markdown in the repository and the next sync updates this site.
{{% /alert %}}

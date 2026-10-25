---
title: API documentation
linkTitle: API documentation
weight: 60
description: >
  A map of the Heimdall API's own documentation site: what each section covers and where to find it, from the endpoint reference to the data-protection documents.
---

The Heimdall API documents itself on its own site,
[docs.artur-rios.tech/heimdall-api](https://docs.artur-rios.tech/heimdall-api/).
This site does not copy that material, because the API's internals change with
the API and the API's site is rebuilt with it. This page is the map: every
section of the API site, what it covers, and a link to it.

The API site's top navigation has five entries: Documentation, Requirements, API
Explorer, Test Coverage and GitHub. The Requirements entry opens the
specification index. Test Coverage opens a coverage report that CI generates
and does not commit.

## Understanding and running the API

| Section | What it covers |
| --- | --- |
| [Home](https://docs.artur-rios.tech/heimdall-api/) | The API's landing page, with an entry point for each of its themes. |
| [Documentation](https://docs.artur-rios.tech/heimdall-api/docs/) | Everything needed to understand, run, test and extend the Heimdall API. |
| [Overview](https://docs.artur-rios.tech/heimdall-api/docs/overview/) | The domain vocabulary (scopes, persons, roles, applications, permissions) and the rules that bind them. |
| [Getting started](https://docs.artur-rios.tech/heimdall-api/docs/getting-started/) | Prerequisites, configuration, migrations and running the API locally. |
| [Architecture](https://docs.artur-rios.tech/heimdall-api/docs/architecture/) | The four layers, the CQRS mediator, the auditing decorator and the HTTP request pipeline. |
| [Domain model](https://docs.artur-rios.tech/heimdall-api/docs/domain-model/) | The entities, their relationships and the deletion cascade rules, as class diagrams. |
| [Operations](https://docs.artur-rios.tech/heimdall-api/docs/operations/) | Migrations, start-up guards, health checks, metrics, logging, rate limiting, data retention and the integrations. |
| [Environments and deployment](https://docs.artur-rios.tech/heimdall-api/docs/environments-and-deployment/) | The four environments and what each PostgreSQL has to allow. |

## Endpoints and the OpenAPI document

| Section | What it covers |
| --- | --- |
| [API reference](https://docs.artur-rios.tech/heimdall-api/docs/api-reference/) | Every endpoint, the role that may call it, and the use case it implements. |
| [API Explorer](https://docs.artur-rios.tech/heimdall-api/docs/api-explorer/) | Swagger UI over the published OpenAPI document. It is read-only: it shows each operation's request and response shapes but does not send requests. |
| [OpenAPI document](https://docs.artur-rios.tech/heimdall-api/openapi/heimdall.json) | The OpenAPI document itself, as raw JSON. |

The API has 61 operations, counted from its controllers; the committed OpenAPI
document has the same 61. They fall into seven groups.

{{% alert title="The reference page is not complete" color="warning" %}}
At API 1.4.0 the API reference page does not list every operation. It omits
`POST /api/auth/register`, `PUT /api/scopes/{id}/self-registration`,
`PUT /api/scopes/{id}/email-links`, `POST /api/auth/2fa/challenge/resend` and
`POST /api/auth/erasure-reconciliation`. The OpenAPI document and the API
Explorer, which is built on it, have all 61.
{{% /alert %}}

| Group | Route | Operations |
| --- | --- | --- |
| Authentication | `api/auth` | 21 |
| Scopes | `api/scopes` | 9 |
| Persons | `api/persons`, `api/scopes/{scopeId}/persons`, `api/scopes/{scopeId}/owners` and related routes | 13 |
| Applications | `api/scopes/{scopeId}/applications` | 6 |
| Scope permissions | `api/scopes/{scopeId}/permissions` | 6 |
| Google users | `api/scopes/{scopeId}/google-users` | 4 |
| Health | `api/healthcheck` | 2 |

## Flows

The flows are sequence diagrams of the paths worth tracing end to end. The
[Flows index](https://docs.artur-rios.tech/heimdall-api/docs/flows/) lists them
all.

| Flow | What it covers |
| --- | --- |
| [Login](https://docs.artur-rios.tech/heimdall-api/docs/flows/login/) | UC-11: password authentication, the uniform rejection and the branch into a two-factor challenge. |
| [Two-factor authentication](https://docs.artur-rios.tech/heimdall-api/docs/flows/two-factor/) | UC-36 to UC-40: setup, confirmation, the challenge-token round trip and recovery codes. |
| [Google sign-in](https://docs.artur-rios.tech/heimdall-api/docs/flows/google-sign-in/) | UC-24 to UC-29: enabling it per scope, sign-up and sign-in, and administering Google users. |
| [Person onboarding](https://docs.artur-rios.tech/heimdall-api/docs/flows/person-onboarding/) | UC-06, UC-14 and UC-15: creating a person, the verification email and replacing a lost link. |
| [Password recovery](https://docs.artur-rios.tech/heimdall-api/docs/flows/password-recovery/) | UC-12 and UC-13: an endpoint designed around what it must not reveal. |
| [Scope permission claims](https://docs.artur-rios.tech/heimdall-api/docs/flows/scope-permission-claims/) | UC-31 to UC-35 and FR-AU-08: how a scope permission ends up inside a JWT. |
| [Audit logging](https://docs.artur-rios.tech/heimdall-api/docs/flows/audit-logging/) | NFR-09: one decorator, every write, no handler changes. |

## Specification

The [Requirements index](https://docs.artur-rios.tech/heimdall-api/docs/requirements/)
lists the specification documents. The same documents, with a one-line summary
each, are also on the [Repositories]({{< relref "/docs/repositories" >}}) page,
linked to GitHub. The API site publishes them in two groups.

### Product and engineering documents

| Document | What it covers |
| --- | --- |
| [Vision Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/vision-document/) | Why Heimdall exists, who it serves, the stakeholders, the goals and what success means. |
| [System Requirements Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/system-requirements-document/) | The functional and non-functional requirements, the data model, the endpoints, the authorization matrix and the deletion strategy. |
| [Use Case Specification Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/use-case-specification-document/) | The actor-facing use cases, with main flows and numbered alternative flows. |
| [Technology Stack Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/technology-stack-document/) | The technologies, the libraries and their pinned versions. |
| [Testing Specification Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/testing-specification-document/) | The unit and functional standards and the required coverage per use case. |
| [Development Workflow Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/development-workflow-document/) | A use case from backlog to merged: branch, issue status, testing gate and pull request. |
| [Operations & Infrastructure Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/operations-infrastructure-document/) | Hosting, the four environments, the technical foundation and the health-check feature. |

### Data-protection documents

Heimdall processes personal data, so its specification includes the documents
that the LGPD and the GDPR call for.

| Document | What it covers |
| --- | --- |
| [Data Protection Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-protection-document/) | Who controls what, on what basis, shared with whom and across which borders: the record of processing under LGPD Art. 37 and GDPR Art. 30. |
| [Data Protection Impact Assessment](https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-protection-impact-assessment/) | The risks to data subjects and their mitigations, under GDPR Art. 35 and LGPD Art. 38. |
| [Data Retention Schedule Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-retention-schedule-document/) | How long each category of personal data is kept, why, and which periods the API enforces. |
| [Privacy Notice](https://docs.artur-rios.tech/heimdall-api/docs/requirements/privacy-notice/) | What Heimdall does with personal data, under LGPD Art. 9 and GDPR Art. 13 and 14. |
| [Data Processing Agreement](https://docs.artur-rios.tech/heimdall-api/docs/requirements/data-processing-agreement/) | The terms for processing a tenant's users' data, under LGPD Art. 39 and GDPR Art. 28. |
| [Incident Response Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/incident-response-document/) | What counts as a personal data breach, who declares one, the clocks that start and who has to be told. |
| [Threat Model Document](https://docs.artur-rios.tech/heimdall-api/docs/requirements/threat-model-document/) | The threats by trust boundary, and the residual risk. |

## Changes and contributing

| Section | What it covers |
| --- | --- |
| [Changelog](https://docs.artur-rios.tech/heimdall-api/docs/changelog/) | The notable changes in each release, rendered from the repository's `CHANGELOG.md`. |
| [Contributing](https://docs.artur-rios.tech/heimdall-api/docs/contributing/) | Build, tests and coverage, migrations, the OpenAPI document, branching and releasing, rendered from `CONTRIBUTING.md`. |
| [Test coverage report](https://docs.artur-rios.tech/heimdall-api/coverage-report/) | The ReportGenerator coverage report, generated in CI. |

{{% alert title="Where this site and the API site differ" color="primary" %}}
This site explains Heimdall as a whole, and covers the UI as well as the API.
The API site is the authority on the API: when the two disagree about an
endpoint, a flow or a requirement, the API site, and ultimately the API's
source, is right.
{{% /alert %}}

---
title: Documentation
linkTitle: Documentation
menu:
  main:
    weight: 10
weight: 20
description: >
  What Heimdall is, how it is put together, how to run it, and how to use it.
---

Heimdall is an identity-management system made of two repositories: the
Heimdall API, which holds the data and the rules, and Heimdall UI, a Flutter
application that drives the API. This documentation covers both. It explains
what Heimdall is, how it is put together, how to run it, how to use the
interface, and how a client system connects to it. The API and the application
each have a section of their own, with the detail the other pages leave out and
their specification documents.

| Section | What it covers |
| --- | --- |
| [Overview]({{< relref "/docs/overview" >}}) | What Heimdall is, what it is not, and the concepts the rest of the documentation assumes. |
| [Architecture]({{< relref "/docs/architecture" >}}) | How the API and the UI are built, and how they talk to each other. |
| [Installation]({{< relref "/docs/installation" >}}) | What you need and the commands to run the API and the UI. |
| [User guide]({{< relref "/docs/user-guide" >}}) | How to use the interface, task by task, by role. |
| [Integrating a client system]({{< relref "/docs/integrating" >}}) | What a system that delegates its identities to Heimdall has to do. |
| [Application documentation]({{< relref "/docs/application" >}}) | Heimdall UI in detail: the scope it acts in, its environments, signing the Android release, the web image's server, use case status and the specification. |
| [API documentation]({{< relref "/docs/api" >}}) | The Heimdall API in detail: the endpoint reference and OpenAPI document, the flows worth tracing, operating the API, test coverage, use case status and the specification. |
| [Repositories]({{< relref "/docs/repositories" >}}) | The repositories behind Heimdall, their releases and the specification documents. |

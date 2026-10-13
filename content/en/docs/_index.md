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
interface, and how a client system connects to it. The API keeps its own
detailed documentation, and these pages link to it rather than copy it.

| Section | What it covers |
| --- | --- |
| [Overview]({{< relref "/docs/overview" >}}) | What Heimdall is, what it is not, and the concepts the rest of the documentation assumes. |
| Architecture | How the API and the UI are built, and how they talk to each other. |
| Installation | What you need and the commands to run the API and the UI. |
| User guide | How to use the interface, task by task, by role. |
| Integrating a client system | What a system that delegates its identities to Heimdall has to do. |
| API documentation | A map of the API's endpoints and a pointer to its reference, explorer and specification. |
| Repositories | The two repositories, their releases and the specification documents. |

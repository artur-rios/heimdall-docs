---
title: Heimdall
linkTitle: Heimdall
---

{{< blocks/cover title="Heimdall" image_anchor="top" height="med" color="dark" >}}
<div class="mx-auto">
  <p class="lead mt-5">One identity service for many systems, with each system's people kept apart.</p>
  <a class="btn btn-lg btn-primary me-3 mb-4" href="{{< relref "/docs" >}}">
    Get started <i class="fas fa-arrow-alt-circle-right ms-2"></i>
  </a>
  <a class="btn btn-lg btn-secondary mb-4" href="https://github.com/artur-rios/heimdall-api">
    Source <i class="fab fa-github ms-2"></i>
  </a>
</div>
{{< /blocks/cover >}}

{{% blocks/lead color="primary" %}}
Heimdall is a centralized identity-management system. It answers one question
for every system that delegates to it: who is this caller, and what are they
allowed to do?

It has two parts: the Heimdall API, built with ASP.NET Core on .NET 10, and
Heimdall UI, a Flutter application that drives it.
{{% /blocks/lead %}}

{{% blocks/section color="dark" type="row" %}}

{{% blocks/feature icon="fa-solid fa-building-shield" title="One scope per client system" %}}
Each client system gets its own scope. Its owners, users, applications and
permissions live inside that scope and stay isolated from every other one.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-users" title="Persons and applications" %}}
Manage human identities as persons, and other systems as applications — a
non-human identity that belongs to one scope.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-key" title="Permissions in the token" %}}
A scope can define its own permissions. Those flagged `IncludeAsJwtClaim` are
added to the JWT issued to people signing in to that scope.
{{% /blocks/feature %}}

{{% /blocks/section %}}

{{% blocks/section color="light" type="row" %}}

{{% blocks/feature icon="fa-solid fa-right-to-bracket" title="Several ways to sign in" %}}
Email and password, Google Sign-In where a scope enables it, and optional
two-factor authentication with an authenticator app, email, or both.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-display" title="One UI, four targets" %}}
Heimdall UI is a single Flutter codebase that ships to the web, Windows, Linux
and Android. What each person sees follows their role.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-scale-balanced" title="Open source" url="https://github.com/artur-rios/heimdall-api/blob/develop/LICENSE" %}}
The default branch of both code repositories is under the Artur Rios Attribution
License. The licence file has the terms.
{{% /blocks/feature %}}

{{% /blocks/section %}}

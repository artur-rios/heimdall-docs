---
title: About Heimdall
linkTitle: About
menu:
  main:
    weight: 40
---

{{< blocks/cover title="About Heimdall" height="auto" color="primary" >}}
An identity service for systems that would otherwise each manage their own users.
{{< /blocks/cover >}}

{{% blocks/lead %}}
Organizations that run several systems often end up with each system managing
its own users, credentials and permissions. The result is duplicated data,
inconsistent security policies and a poor experience for the people signing in.

Heimdall replaces that with one multi-tenant identity service, with a clear
boundary around each client system. The API provides it, but on its own it has
no interface, so every task means composing HTTP requests by hand. Heimdall UI
puts a task-shaped screen in front of each use case the API exposes.
{{% /blocks/lead %}}

{{% blocks/section color="dark" type="row" %}}

{{% blocks/feature icon="fa-solid fa-server" title="API (.NET)" url="https://github.com/artur-rios/heimdall-api" %}}
The identity-management API, built with ASP.NET Core on .NET 10.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-mobile-screen-button" title="UI (Flutter)" url="https://github.com/artur-rios/heimdall-ui" %}}
The front-end for the API, for the web, Windows, Linux and Android.
{{% /blocks/feature %}}

{{% blocks/feature icon="fa-solid fa-scale-balanced" title="Licence" url="https://github.com/artur-rios/heimdall-api/blob/develop/LICENSE" %}}
The Artur Rios Attribution License: free and open source, so you may view, use,
fork, modify and extend it, crediting the author.
{{% /blocks/feature %}}

{{% /blocks/section %}}

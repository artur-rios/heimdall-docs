---
title: 'API explorer'
linkTitle: 'API explorer'
weight: 61
description: 'Swagger UI over the published OpenAPI document — every endpoint, its schema, and its authorization.'
---

Every endpoint the API exposes, rendered from
[the published OpenAPI document](../../../api/openapi/heimdall.json). The document is generated from
the controllers themselves — the summaries below are the ones in the source — and regenerated with
`python scripts/openapi.py`. It is byte-for-byte what a running instance serves at
`/swagger/v1/swagger.json`: both come from the same `SwaggerConfiguration`.

{{% alert title="This explorer does not call anything" color="info" %}}
The page has no server behind it, so **Try it out** and **Authorize** are both gone — a token entered
here could only be attached to a request, and no request can be sent. The padlocks stay, because
which endpoints need one is worth knowing. To call the endpoints, run the API and use its own Swagger
UI at `/swagger` — same document, with **Authorize** and **Try it out** working — or the
[`.http` files or Bruno collection](../../installation/) in
`api-client/`. For what each endpoint means and who may call it in prose, see the
[API reference](../reference/).
{{% /alert %}}

{{< swagger-ui >}}

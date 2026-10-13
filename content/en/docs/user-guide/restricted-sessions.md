---
title: Restricted sessions
linkTitle: Restricted sessions
weight: 30
description: >
  The one screen available when processing of your account is restricted at your own request: lift the restriction, download your data, request erasure, or sign out.
---

Under data-protection law (LGPD and GDPR), a person can ask for the processing of
their data to be restricted. While a restriction is in place, Heimdall keeps the
data as it is and uses it for nothing else. The API enforces this: when someone
whose processing is restricted signs in, it issues a token that admits only that
person's own data-protection rights and refuses everything else.

Heimdall UI recognises that situation and gives the person a single screen
instead of the usual application, where every request would fail.

**Who can reach it:** a restricted subject, that is a person of any role or a
Google user whose processing is restricted at their own request. A full session
that asks for the screen is sent to Home. A restricted session can open this
screen and the privacy notice, and nothing else. The UI can lift a restriction
but cannot impose one; imposing one is done through the API (see
[What the UI does not cover]({{< relref "/docs/user-guide#what-the-ui-does-not-cover" >}})).

## UI-30: Use a restricted session

Screen: `/restricted`, titled "Restricted account".

1. Sign in as usual with your password, with the second factor if you have one, or
   with Google. See [Signing in]({{< relref "/docs/user-guide/signing-in" >}}).
2. The API answers with a token and says processing is restricted. The UI starts
   a session marked as subject-rights-only.
3. The UI sends you to the restricted-account screen.
4. The screen says plainly that processing of your account is restricted at your
   request and that only four actions are available: lift the restriction,
   download your data, request erasure, and sign out. It links the privacy notice.

**Lift the restriction**

1. Choose **Lift the restriction** and confirm.
2. The UI asks the API to lift it, naming you.
3. The UI ends the session and returns to the sign-in screen, which says the
   restriction is lifted and that you should sign in again for full access.

**Download my data**

1. Choose **Download my data**.
2. The UI asks the API for a copy of everything Heimdall holds about you.
3. The UI saves it as an indented JSON file named
   `heimdall-data-export-<date>-<time>.json`. On the web the browser offers it as
   a download. On every other target it is written to the downloads folder. The UI
   tells you where it went.

**Request erasure**

1. Choose **Request erasure**. A dialog says erasure cannot be undone.
2. A person confirms with their password. A Google user confirms by signing in with
   Google again.
3. The UI sends the request to the API.
4. The API records the request and its deadline. The UI says so and gives the
   deadline. While processing is restricted, your data is kept as it is and the
   erasure is carried out once the restriction is lifted. You stay on the screen.

Other things that can happen:

- **You return later.** A stored token that carries the subject-rights-only claim
  is restored as a restricted session, so you land on this screen again.
- **The restriction was already lifted elsewhere.** The outcome you wanted holds,
  so the session ends as in step 3 of lifting.
- **A request is refused, or the API cannot be reached.** The API's messages, or a
  note that the API could not be reached, are shown. The session and the screen
  stay as they were and you can try again.
- **The device would not keep the file.** The UI says so and nothing else changes.
- **The erasure password is wrong.** The API's message is shown and the session
  stays: a mistyped password is not a rejected token.
- **The erasure is recorded but blocked.** This usually happens when you are the
  last owner of a scope. The UI says the request is recorded and its deadline runs,
  and gives the API's reason for not suspending the account yet.
- **Erasure was already requested.** The API's messages are shown.
- **A Google user whose device cannot run Google's flow.** The build has no Google
  client ID, or the target cannot run Google's sign-in. Erasure needs a fresh
  Google sign-in, so the action is disabled and the screen says to request it from
  a device where you can sign in with Google.
- **You dismiss a confirmation or back out of Google's flow.** Nothing is sent and
  nothing changes.
- **Signing out.** **Sign out** works as from any session. For a Google user the
  API's Google sign-out is not called, because a subject-rights-only token is not
  admitted to it.

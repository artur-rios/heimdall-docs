---
title: Signing in
linkTitle: Signing in
weight: 10
description: >
  Sign in with an email and a password, complete the second factor, sign in with Google, and how the UI decides which screens you may open.
---

This page covers getting into Heimdall UI. If you cannot sign in because you
forgot the password or have not verified your address, see
[Password and email]({{< relref "/docs/user-guide/password-and-email" >}}).

**Who can reach it:** anyone who is not signed in. The second-factor screen
opens only while you hold a challenge from a sign-in that asked for one. Once you
are signed in, asking for the sign-in screen sends you to Home. The last section,
about how routes are guarded, applies to everyone.

## UI-01: Login

Screen: `/login`. Actor: anyone who is not signed in.

1. Open the application. Without a session you are redirected to the sign-in
   screen.
2. Enter your email address and your password.
3. Press **Sign in**.
4. On success the UI stores the token, starts your session and takes you to the
   screen you originally asked for, or to Home.

The sign-in screen also has **Forgot your password?** and a **Privacy notice**
link.

Other things that can happen:

- **Wrong credentials.** The API's messages are shown above the form. The email
  stays and the password is cleared.
- **Empty or malformed email, or empty password.** The form marks the field and
  sends nothing.
- **Two-factor authentication is on for you.** Instead of a session you are taken
  to the second-factor screen (next section).
- **The API cannot be reached.** A banner offers a retry and nothing changes.
- **Google Sign-In is available.** The screen also shows the Google control
  (see the Google section below).

## UI-02: Complete two-factor challenge at login

Screen: `/login/two-factor`, titled "Two-step verification". Actor: a person
holding a challenge from the previous step.

1. The screen names the method in use.
2. Enter the code from your authenticator application, from the email the API
   sent you, or one of your recovery codes.
3. Press **Verify**. The UI sends the challenge and the code to the API.
4. On success the UI stores the token, starts your session and takes you onward.

Other things that can happen:

- **Wrong code.** The API's messages are shown, and the challenge stays open so
  you can try again.
- **The challenge expired or was rejected.** The challenge is discarded and you
  are returned to the sign-in screen, which says the sign-in must restart.
- **More than one method is available.** A selector lets you switch between them
  for the length of the challenge. **Use a recovery code instead** switches the
  field to a recovery code, and **Back to sign in** abandons the challenge.
- **You used a recovery code.** After it works, a message tells you the code is
  spent and points you to your security settings to generate new ones (see
  [Your account]({{< relref "/docs/user-guide/your-account" >}})).
- **You leave the screen.** The challenge is discarded and you are signed out of
  the attempt. It is never stored.

## UI-06: Sign in and sign out with Google

Screen: `/login`. Actors: anyone who is not signed in, and Google users.

This works only if the UI build has a Google client ID and the scope has Google
Sign-In switched on (see [Scopes]({{< relref "/docs/user-guide/scopes" >}})). How
a build is told which scope it acts in is described in
[Architecture]({{< relref "/docs/architecture#configuration-and-secure-storage" >}}).

Signing in:

1. The sign-in screen shows a Google control beside the email and password form.
   On the web it is Google's own button. On the other targets it reads **Continue
   with Google**.
2. Use it and complete Google's own sign-in.
3. Google returns a signed ID token to the UI, which sends it to the API together
   with the scope.
4. The API answers with a Heimdall token. The UI stores it, starts your session
   and takes you onward.

Signing out:

1. A Google user presses the **Sign out** icon in the top bar of any signed-in
   screen.
2. The UI tells the API, clears the local Google session, discards the token and
   returns to the sign-in screen.

Other things that can happen:

- **Not configured.** With no Google client ID in the build, the control is hidden
  rather than shown broken.
- **Google Sign-In is off for the scope, or the API rejects the token.** The
  API's messages are shown and the email and password form stays available.
- **You cancel Google's own flow.** Nothing is sent and the screen is unchanged.
- **The target cannot run Google's flow.** The control is hidden, and the
  credentials form is the only way in.

## UI-07: Guard routes by session and role

Actor: everyone. The UI checks every route, whether you navigate to it or open
its URL directly. On the web the routes are paths, so the links in emails open
the right screen.

1. The UI decides whether the route is public (sign-in, password recovery and
   reset, email verification, the second-factor screen and the privacy notice) or
   private.
2. It reads your session state.
3. If you are signed in with a role that may use the route, you reach it.

What happens when you cannot:

- **No session.** A private route sends you to the sign-in screen and remembers
  where you were going, so you land there after signing in.
- **A challenge is in progress.** Every route except the second-factor screen
  sends you back to it.
- **The session is being restored.** While the stored token is read at start-up,
  the UI shows a loading state and does not redirect, so a slow read cannot send
  you to the sign-in screen.
- **Your role cannot use the screen.** You see a "Not available for your role"
  screen with a **Back to home** button, not a redirect loop. Nothing is wrong
  with your session.
- **The API rejects your token.** The session ends and you are sent to the
  sign-in screen, which says the session ended. A refused password or code that
  you typed into a request is not a rejected token and leaves the session alone.
- **You are already signed in.** Asking for the sign-in or second-factor screen
  sends you to Home.
- **The stored token has expired.** It is discarded at start-up without calling
  the API.
- **Your session is a restricted one.** Every route except the restricted-session
  screen and the privacy notice sends you to the restricted-session screen (see
  [Restricted sessions]({{< relref "/docs/user-guide/restricted-sessions" >}})).
  A full session asking for that screen is sent to Home.

The table of which role reaches which page is on the
[User guide]({{< relref "/docs/user-guide" >}}) index.

---
title: Your account
linkTitle: Your account
weight: 40
description: >
  View and edit your own profile, and turn two-factor authentication on and off, with its recovery codes.
---

Every signed-in person, whatever the role, has a profile and security settings of
their own. Open them with the **Profile** destination in the navigation, or from the
account tiles on Home, each of which opens the screen where that detail is
changed.

**Who can reach it:** System Admin, Scope Admin and User, with a full session. A
restricted session cannot open these screens.

## UI-08: View and edit own profile

Screen: `/profile`.

1. Open **Profile**.
2. The UI loads your record and shows your name and email, with your role, whether
   your email is verified, your scope (or "Not a member of a scope") and, if you
   own any, the scopes you own.
3. Press **Edit**, change your name or your email, and press **Save changes**.
4. The UI sends the change to the API and shows the updated record.

Other things that can happen:

- **Empty name or malformed email.** The form blocks submission.
- **The update is rejected.** For example, the email is already taken. The API's
  messages are shown against the field and what you typed is kept.
- **You changed your email.** The API marks the new address unverified. The UI
  says so and offers **Send verification email** (see
  [Password and email]({{< relref "/docs/user-guide/password-and-email" >}})).
- **Nothing changed.** **Save changes** stays disabled until a field differs, and
  says "No changes to save yet."
- **Your record is gone.** If the API answers that the person no longer exists,
  because it was deleted while you were signed in, the UI signs you out and
  explains why.

## UI-09: Manage two-factor authentication

Screen: `/profile/security`, reached from the **Security** entry on the profile.
The screen opens by saying whether two-factor authentication is on or off.

Two-factor authentication is available to persons. A Google user sees "Not
available for this account" instead: Google carries its own second factor.

**Turn it on**

1. Under **Turn it on**, choose a method: **Authenticator app** or **Emailed
   code**.
2. For an authenticator app, the UI shows a QR code and, beside it, the setup key
   as selectable text so you can type it in by hand. For the emailed code, the UI
   says a code has been sent.
3. Enter the code from your authenticator or your inbox and press **Confirm**.
4. The API confirms and returns your recovery codes. The UI shows them once, with
   a **Copy codes** button, and you must press **I have saved my codes** before
   you can move on.

**Turn it off**

1. Press **Turn off two-factor** and confirm.
2. Enter your current password and a second factor, either a generated code or a
   recovery code. The API requires both and refuses either alone.
3. The screen returns to the "off" state.

**Generate new recovery codes**

1. Press **Generate new codes** and confirm that the current codes stop working
   immediately.
2. Enter a second factor in the dialog: a generated code or a recovery code. No
   password is asked for.
3. The UI shows the new codes once, under the same rule: press **I have saved my
   codes** to continue.

Other things that can happen:

- **Wrong confirmation code.** The API's messages are shown and the setup stays
  open so you can try again without starting over.
- **You leave before confirming.** Two-factor authentication stays off and the
  pending secret is discarded from memory.
- **You try to leave before acknowledging the recovery codes.** The UI asks first,
  because the codes are shown exactly once.
- **Turning it off is rejected.** The API's messages are shown and the feature
  stays on.
- **The QR code cannot be drawn.** The UI says so and asks you to enter the setup
  key by hand, so a rendering failure never blocks setup.

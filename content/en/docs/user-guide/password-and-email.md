---
title: Password and email
linkTitle: Password and email
weight: 20
description: >
  Recover a forgotten password, set a new one from the emailed link, and verify an email address.
---

These three tasks are reached from links, mostly in emails the API sends. They
are public: you do not need to be signed in to recover a password or to open a
verification link.

**Who can reach it:** anyone, signed in or not. These screens stay open when you
have a session. Asking for a new verification email needs a signed-in session
(see below). A restricted session cannot open them.

## UI-03: Request password recovery

Screen: `/password-recovery`, reached from **Forgot your password?** on the
sign-in screen. Actor: anyone who is not signed in.

1. Open the password recovery screen from the sign-in screen.
2. Enter your email address.
3. Press **Send reset link**.
4. The UI shows "Check your inbox", telling you to look for a link. It is the same
   message whether or not the address belongs to an account. This is deliberate:
   the UI must not reveal which addresses are registered.

Other things that can happen:

- **Empty or malformed address.** The form blocks submission.
- **The API cannot be reached.** A banner offers a retry. The confirmation is not
  shown, because nothing was sent.
- **You press the button twice.** The button is disabled while a request is in
  flight, so only one request is sent.

## UI-04: Reset password

Screen: `/password-reset?token=...`, titled "Set a new password". Actor: anyone
holding a reset token, normally by following the link in the recovery email.

1. Open the link from the email. The UI takes the token from the link.
2. Enter a new password and confirm it. A new password needs at least 8
   characters.
3. Press **Set password**. The UI sends the token and the new password to the API.
4. The UI says your password is set and offers **Sign in**.

Other things that can happen:

- **The link has no token.** The screen says the link is incomplete, notes that
  mail clients sometimes cut long links short, and offers **Request a new link**.
- **The token is invalid or expired.** The API's messages are shown and you can
  request a new link.
- **The two passwords differ.** The form marks the confirmation field and sends
  nothing.
- **The password is rejected.** The API's messages are shown against the password
  field.

## UI-05: Verify email and resend verification

Screen: `/verify-email?token=...`. Actor: anyone with a verification token, signed
in or not.

1. Open the link from the verification email. The UI takes the token from the
   link.
2. It sends the token to the API at once and shows "Checking your link".
3. When the API confirms, the screen says your email is verified. **Continue**
   takes you to Home if you have a session. **Sign in** takes you to the sign-in
   screen if you do not.

Other things that can happen:

- **The link has no token.** The screen says the link is incomplete and offers to
  send a new email.
- **The token is invalid or expired.** The API's messages are shown and the screen
  offers to send a new email.
- **Asking for a new email.** Press **Send a new email**. The UI asks the API for
  a fresh verification email and says it is on its way. The API sends it to the
  address of the signed-in account, so this works only while you are signed in. If
  you are not, the screen asks you to sign in first.
- **The address is already verified.** This counts as success and the screen says
  so.
- **A signed-in account with an unverified address.** A dismissible banner at the
  top of the signed-in screens says "Your email address is not verified yet" and
  has a **Resend** button.

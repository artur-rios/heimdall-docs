---
title: Google users
linkTitle: Google users
weight: 90
description: >
  Browse the Google users of a scope and delete them, logically or permanently.
---

A Google user is an identity authenticated by Google instead of a password. It
always has the User role and belongs to one scope. It is created the first time
someone signs in to the scope with Google, which needs Google Sign-In to be
switched on for the scope (see
[Scopes]({{< relref "/docs/user-guide/scopes" >}})). The Google users screens work
inside one scope. Open a scope and press **Google users**.

**Who can reach it:** System Admin, and Scope Admin for the scopes they own. A User
does not see these screens. The details of a Google user come from Google, so the
UI never lets anyone edit them.

## UI-28: Browse and view Google users

Screens: `/scopes/:scopeId/google-users` for the list, and
`/scopes/:scopeId/google-users/:googleUserId` for one user.

1. Open **Google users** from the scope's detail.
2. The UI asks the API for a page of the scope's Google users, using the page, page
   size, filters and the **Include deleted** switch.
3. The page shows each user's name, email, profile picture, whether Google verified
   the email, and whether the user is active or deleted.
4. Page through the list, search with **Search by name** and **Search by email**
   then press **Search**, or switch **Include deleted**.
5. Press a user to open the full record. It shows the name and email, the user's
   identifier, the Google identifier, whether Google verified the email, the scope
   and the state.

Other things that can happen:

- **Empty list.** The screen explains that a Google user appears only after someone
  signs in to the scope with Google. If the scope has Google Sign-In switched off,
  it says so and offers **Scope settings**. "No Google users matched" offers
  **Clear filters**.
- **The request fails.** An error panel shows the API's messages and offers a retry.
- **You may not see this scope.** The "Not available for your role" panel is shown.
- **The picture is missing or unreachable.** An avatar with the user's initials
  stands in, so the row never breaks.
- **Editing.** There is none. The record says its details come from Google and
  cannot be changed here.

## UI-29: Delete a Google user, logically and permanently

Screen: `/scopes/:scopeId/google-users/:googleUserId`, in the "Delete this Google
user" section at the bottom. A System Admin can do both kinds of deletion. A Scope
Admin can do the logical one only.

Logical deletion:

1. Press **Delete Google user** and confirm in a dialog that names the user.
2. The UI deletes the user and returns to the list.

Permanent deletion (System Admin):

1. Press **Delete permanently**. The dialog asks you to type the user's email
   address.
2. Confirm. The UI deletes the user and returns to the list.

Other things that can happen:

- **You cancel.** Nothing is sent.
- **The API refuses.** Its messages are shown and the record stays open.
- **The typed email does not match.** The confirm button stays disabled.
- **You are a Scope Admin.** You never see the permanent deletion control.
- **The person can sign in again.** Both dialogs say that while the scope has
  Google Sign-In on, a deleted Google user can sign in again and a new record
  appears. To stop that, switch Google Sign-In off for the scope.

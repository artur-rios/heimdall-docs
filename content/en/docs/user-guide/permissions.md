---
title: Scope permissions
linkTitle: Scope permissions
weight: 80
description: >
  Browse, create, update and delete the named permissions of a scope, and choose whether each one goes into tokens.
---

A scope can define named permissions, each with a description and a flag saying
whether it is included in tokens as a claim. When a token is issued, the names of
the flagged permissions are added to it, so a client system can read them without
asking the API again. The claim is a snapshot, so a change shows up in tokens
issued from then on. The permissions screens work inside one scope. Open a scope
(see [Scopes]({{< relref "/docs/user-guide/scopes" >}})) and press **Permissions**.

**Who can reach it:** System Admin, and Scope Admin for the scopes they own. A User
does not see these screens.

## UI-24: Browse scope permissions

Screen: `/scopes/:scopeId/permissions`.

1. Open **Permissions** from the scope's detail.
2. The UI asks the API for a page of the scope's permissions, using the page, page
   size, filters and the **Include deleted** switch.
3. The page shows each permission's name and description, whether it is included in
   tokens ("In tokens": Yes or No), and whether it is active or deleted.
4. Page through the list, search with **Search by name**, or switch **Include
   deleted**.

Other things that can happen:

- **Empty list.** "No permissions yet" offers **New permission**. "No permissions
  matched" offers **Clear filters**.
- **The request fails.** An error panel shows the API's messages and offers a retry.
- **You may not see this scope.** The "Not available for your role" panel is shown.

## UI-25: Create a scope permission

Screen: `/scopes/:scopeId/permissions/new`. A Scope Admin can only create within a
scope they own.

1. Press **New permission**.
2. Enter a name and a description, and choose whether the permission is included
   in tokens with the **Include in tokens** switch.
3. Press **Create permission**.
4. The API creates it. The UI confirms and opens its detail.

Other things that can happen:

- **Empty name.** Submission is blocked.
- **The name already exists in the scope.** The API's messages are shown against
  the name.
- **You cancel a modified form.** The UI asks for confirmation first.
- **What the switch means.** The form says that every token the scope issues from
  now on carries the permission as a claim, so its applications can read it without
  asking the API again.

## UI-26: View and update a scope permission

Screen: `/scopes/:scopeId/permissions/:permissionId`.

1. Open a permission from the list, or by its URL.
2. The UI loads and shows it.
3. Press **Edit**, change the name, the description or the **Include in tokens**
   switch, and press **Save changes**.
4. The UI sends the change to the API and shows the updated record.

Other things that can happen:

- **The permission does not exist.** A not-found panel offers a way back.
- **The API answers that you may not.** The "Not available for your role" panel is
  shown.
- **The update is rejected.** The API's messages are shown against the field.
- **The permission is deleted.** It is shown read-only, marked as deleted.
- **You changed the switch.** After saving, the screen says that tokens issued from
  then on carry the change, and that tokens already issued do not change: they
  still carry the permission until they expire if you turned it off, and do not
  carry it if you turned it on.

## UI-27: Delete a scope permission, logically and permanently

Screen: `/scopes/:scopeId/permissions/:permissionId`, at the bottom of the detail.
A System Admin can do both kinds of deletion. A Scope Admin can do the logical one
only.

Logical deletion:

1. Press **Delete permission** and confirm in a dialog that names the permission.
2. The UI deletes it and returns to the list.

Permanent deletion (System Admin):

1. Press **Delete permanently**. The dialog asks you to type the permission's name.
2. Confirm. The UI deletes it and returns to the list.

Other things that can happen:

- **You cancel.** Nothing is sent.
- **The API refuses.** Its messages are shown and the permission stays open.
- **The typed name does not match.** The confirm button stays disabled.
- **You are a Scope Admin.** You never see the permanent deletion control.

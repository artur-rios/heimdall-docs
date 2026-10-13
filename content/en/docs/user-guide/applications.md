---
title: Applications
linkTitle: Applications
weight: 70
description: >
  Browse, create, update and delete the applications of a scope.
---

An application is a non-human identity, usually another system, that uses a scope
for its identity. It lives in one scope and has an owner. The applications screens
work inside one scope. Open a scope (see
[Scopes]({{< relref "/docs/user-guide/scopes" >}})) and press **Applications**.

**Who can reach it:** System Admin, and Scope Admin for the scopes they own. A User
does not see these screens.

## UI-20: Browse applications in a scope

Screen: `/scopes/:scopeId/applications`.

1. Open **Applications** from the scope's detail.
2. The UI asks the API for a page of the scope's applications, using the page, page
   size, filters and the **Include deleted** switch.
3. The page shows each application's name, its owner and whether it is active or
   deleted.
4. Page through the list, search with **Search by name**, or switch **Include
   deleted**.

Other things that can happen:

- **Empty list.** "No applications yet" offers **New application**. "No
  applications matched" offers **Clear filters**.
- **The request fails.** An error panel shows the API's messages and offers a retry.
- **You may not see this scope.** The "Not available for your role" panel is shown.
- **An owner cannot be resolved to a person.** The row shows the owner's identifier
  instead of a name, so the row never goes blank.

## UI-21: Create an application

Screen: `/scopes/:scopeId/applications/new`. A Scope Admin can only create within a
scope they own.

1. Press **New application**.
2. Enter a name and choose an owner. The owner must be one of the scope's owners.
   A Scope Admin is offered only themselves, because that is the only owner the API
   accepts from them.
3. Press **Create application**.
4. The API creates the application. The UI confirms and opens its detail.

Other things that can happen:

- **Empty name, or no owner.** Submission is blocked and the form says which. If
  the scope has nobody who could own an application, the form says so.
- **The name already exists in the scope.** The API's messages are shown against the
  name.
- **The owner is refused.** The API's messages are shown against the owner
  selector. The selector lists only people who can own an application in the scope,
  which avoids most refusals.
- **You cancel a modified form.** The UI asks for confirmation first.

## UI-22: View and update an application

Screen: `/scopes/:scopeId/applications/:applicationId`.

1. Open an application from the list, or by its URL.
2. The UI shows its name, its owner, its identifier, its scope and its state.
3. Press **Edit**, change the name or the owner, and press **Save changes**.
4. The UI sends the change to the API and shows the updated record.

Other things that can happen:

- **The application does not exist.** An "Application not found" panel offers a way
  back.
- **The API answers that you may not.** The "Not available for your role" panel is
  shown.
- **The update is rejected.** The API's messages are shown against the field.
- **The application is deleted.** It is shown read-only, marked as deleted.
- **Nothing changed.** **Save changes** stays disabled until a field differs.

## UI-23: Delete an application, logically and permanently

Screen: `/scopes/:scopeId/applications/:applicationId`, in the "Delete this
application" section at the bottom. A System Admin can do both kinds of deletion.
A Scope Admin can do the logical one only.

Logical deletion:

1. Press **Delete application** and confirm in a dialog that names it.
2. The UI deletes it and returns to the list.

Permanent deletion (System Admin):

1. Press **Delete permanently**. The dialog asks you to type the application's name.
2. Confirm. The UI deletes it and returns to the list.

Other things that can happen:

- **You cancel.** Nothing is sent.
- **The API refuses.** Its messages are shown and the application stays open.
- **The typed name does not match.** The confirm button stays disabled.
- **You are a Scope Admin.** You never see the permanent deletion control.

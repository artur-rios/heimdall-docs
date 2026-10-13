---
title: Scopes
linkTitle: Scopes
weight: 50
description: >
  Browse, create, update and delete scopes, manage their owners, and switch Google Sign-In on or off.
---

A scope is the tenant boundary of one client system. It holds that system's
owners, users, applications, permissions and Google users. Everything else in the
administration screens (persons, applications, permissions, Google users) lives
inside a scope, and you reach it from the scope's detail screen.

**Who can reach it:** System Admin and Scope Admin. A System Admin sees and manages
every scope. A Scope Admin sees and manages only the scopes they own, cannot create
or delete a scope, and sees a scope's name and description read-only. A User does
not see these screens.

## UI-10: Browse and search scopes

Screen: `/scopes`, the **Scopes** destination in the navigation.

1. Open **Scopes**.
2. The UI asks the API for a page of scopes, using the current page, page size,
   search text and the **Include deleted** switch.
3. The page is shown as cards on a narrow window and as a table on a wide one. Each
   scope shows its name and description, its Google Sign-In state (On or Off), its
   owner count and whether it is active or deleted. Press a scope to open it.
4. Page through the list, search by name with **Search by name**, or switch
   **Include deleted** to see deleted scopes.

Other things that can happen:

- **Empty list.** "No scopes yet" explains what a scope is and, for a System
  Admin, offers **New scope**. "No scopes matched" offers **Clear filters**.
- **The request fails.** An error panel shows the API's messages and a retry
  button. Your filters are kept.
- **You are a Scope Admin.** The list contains only the scopes you own and there
  is no **New scope** button.
- **Changing the search or the switch** returns to the first page.
- **Loading.** A placeholder holds the place of the list so the layout does not
  jump.

## UI-11: Create a scope

Screen: `/scopes/new`. Actor: System Admin.

1. From the scopes list, press **New scope**.
2. Enter a name and a description, and add at least one owner. Press **Add owner**
   to pick a Scope Admin or a System Admin, or press **Add me** to add yourself.
   **Add me** is what makes a first scope possible before any Scope Admin exists.
3. Press **Create scope**.
4. The API creates the scope. The UI confirms and opens the new scope's detail.

Other things that can happen:

- **Empty name, or no owner.** Submission is blocked. Each refused field shows its
  message and the first one is scrolled into view. With no owner the form says to
  add at least one.
- **The name already exists.** The API's messages are shown against the name and
  the rest of the form is kept.
- **An owner is rejected.** The API only accepts a Scope Admin or a System Admin
  as an owner. Its messages are shown against the owner selector.
- **You cancel a modified form.** The UI asks for confirmation first.
- **The request fails for transport reasons.** The form stays filled in and offers
  a retry.

## UI-12: View and update a scope

Screen: `/scopes/:scopeId`. A Scope Admin can only open a scope they own.

1. Open a scope from the list, or by its URL.
2. The UI shows the scope: its name and description, its scope ID with a copy
   button, its Google Sign-In switch, how many owners it has, and links to its
   Owners, Persons, Applications, Permissions and Google users. A client system
   needs the scope ID to create and authenticate its users.
3. A System Admin presses **Edit**, changes the name or the description and presses
   **Save changes**.
4. The UI sends the change to the API and shows the updated record.

Other things that can happen:

- **The scope does not exist.** A "Scope not found" panel offers a way back to the
  list.
- **The API answers that you may not.** The "Not available for your role" panel
  is shown.
- **The update is rejected.** For example, the name is a duplicate. The API's
  messages are shown against the field.
- **The scope is deleted.** It is shown read-only and marked as deleted.
- **Nothing changed.** **Save changes** stays disabled until a field differs.
- **You are a Scope Admin.** The name and description are shown read-only and
  there is no **Edit** button, because only a System Admin may update them. The
  Google Sign-In switch and the owners remain yours to change.

## UI-13: Delete a scope, logically and permanently

Screen: `/scopes/:scopeId`, in the "Delete this scope" section at the bottom.
Actor: System Admin.

Logical deletion:

1. Press **Delete scope**.
2. A confirmation dialog names the scope and explains that the record is kept and
   can be restored by the API.
3. Confirm. The UI deletes the scope and returns to the list with a confirmation.

Permanent deletion:

1. Press **Delete permanently**.
2. A confirmation dialog names the scope and says the scope and everything in it,
   its persons, applications, permissions and Google users, are erased. It asks you
   to type the scope's name before the confirm button works.
3. Confirm. The UI deletes the scope and returns to the list with a confirmation.

Other things that can happen:

- **You cancel.** The dialog closes and nothing is sent.
- **The API refuses.** For example, the scope still holds users. Its messages are
  shown and the scope stays open.
- **The typed name does not match.** The confirm button stays disabled.
- **The scope is already deleted.** The UI treats it as done and returns to a
  refreshed list.
- **You are a Scope Admin.** Neither button is shown.

## UI-14: Manage scope owners

Screen: `/scopes/:scopeId/owners`, from the **Owners** link on the scope's detail.
A Scope Admin can only manage the scopes they own.

1. Open **Owners**. The UI lists the scope's current owners.
2. To add an existing Scope Admin as a co-owner (or, as a System Admin, an existing
   System Admin), press **Add existing** and pick the person.
3. To create a brand-new Scope Admin as a co-owner, press **Create owner**, fill
   in a name, an email and a password, and press **Create**.
4. To promote an existing user of the scope, find them under **Promote a user** and
   press **Promote**. A confirmation explains that the person stops being a user of
   the scope and becomes a Scope Admin and co-owner.
5. To remove an owner, press the remove icon beside them and confirm.

Other things that can happen:

- **It is the last owner.** The API refuses to remove the only owner. The remove
  button is disabled when the list has a single owner.
- **The person is not a Scope Admin.** The API refuses and its messages are shown.
- **The person is already an owner.** The API refuses a duplicate, and people who
  already own the scope are left out of the picker.
- **Creating a co-owner fails validation.** An empty name, a malformed email or a
  rejected password shows the API's messages against the field. The dialog stays
  open with what you typed.
- **You cancel a promotion.** The dialog closes and nothing is sent.
- **You remove yourself.** A Scope Admin removing their own ownership is warned
  that they lose access to the scope, and the screen refreshes accordingly.

## UI-15: Toggle Google Sign-In for a scope

Screen: `/scopes/:scopeId`, the **Google Sign-In** switch. A Scope Admin can change
it for a scope they own.

1. The scope detail shows a switch that reflects whether Google Sign-In is on. When
   it is off the text reads "Google sign-in is off for this scope."
2. Flip the switch.
3. The UI sends the new value to the API.
4. The switch settles on the state the API confirms.

Other things that can happen:

- **The API refuses.** The switch returns to its previous state and the API's
  messages are shown.
- **You turn it off while Google users exist.** Before anything is sent, a dialog
  titled "Turn Google Sign-In off?" says how many Google accounts in the scope will
  no longer be able to sign in.
- **A request is in flight.** The switch is disabled until it finishes, so it cannot
  be flipped twice.

Google Sign-In is off by default. The people who sign in with it appear under
[Google users]({{< relref "/docs/user-guide/google-users" >}}).

---
title: Persons
linkTitle: Persons
weight: 60
description: >
  Browse, create, update and delete the people of a scope.
---

A person is a human identity with a name, an email, a role and a password. The
persons screens work inside one scope. Open a scope (see
[Scopes]({{< relref "/docs/user-guide/scopes" >}})) and press **Persons**.

**Who can reach it:** System Admin, and Scope Admin for the scopes they own. A Scope
Admin who opens a scope they do not own gets the "Not available for your role"
panel. A User does not see these screens.

## UI-16: Browse and search persons in a scope

Screen: `/scopes/:scopeId/persons`.

1. Open **Persons** from the scope's detail.
2. The UI asks the API for a page of the scope's persons, using the page, page size,
   filters and the **Include deleted** switch.
3. The page shows each person's name, email, role, whether the email is verified,
   and whether the person is active or deleted.
4. Page through the list, search with **Search by name** and **Search by email**
   then press **Search**, or switch **Include deleted**.

Other things that can happen:

- **Empty list.** "No persons yet" offers **New person**. "No persons matched"
  offers **Clear filters**.
- **The request fails.** An error panel shows the API's messages and offers a retry.
- **You are a Scope Admin and do not own the scope.** The "Not available for your
  role" panel is shown, with a button back to the scopes.
- **Changing a filter** returns to the first page.

## UI-17: Create a person

Screen: `/scopes/:scopeId/persons/new`. A Scope Admin can only create within a
scope they own.

1. Press **New person**.
2. Enter a name, an email, a password of at least 8 characters, and a role.
3. Press **Create person**.
4. The API creates the person and sends the verification email. The UI confirms and
   opens the new person's detail.

Which roles you can choose depends on who you are. A Scope Admin can create Users
only, so the role list has one entry. A System Admin can create a User, a Scope
Admin or a System Admin. A User belongs to the scope you opened the form in. A Scope
Admin or a System Admin belongs to no scope, and the form says so; it is created
through a System Admin-only route in the API.

Other things that can happen:

- **Empty name, malformed email or empty password.** Submission is blocked.
- **The email is already registered.** The API's messages are shown against the
  email field.
- **The password is rejected by policy.** The API's messages are shown against the
  password field.
- **The role is not permitted.** A Scope Admin is not offered anything but User. A
  refusal from the API is shown as returned.
- **You cancel a modified form.** The UI asks for confirmation first.

## UI-18: View and update a person

Screen: `/scopes/:scopeId/persons/:personId`.

1. Open a person from the list, or by their URL.
2. The UI shows the record: name, email, role, scope membership, the scopes they
   own and whether the email is verified.
3. Press **Edit**, change the name or the email, and press **Save changes**.
4. The UI sends the change to the API and shows the updated record.

Other things that can happen:

- **The person does not exist.** A not-found panel offers a way back.
- **The API answers that you may not.** The "Not available for your role" panel is
  shown.
- **The update is rejected.** The API's messages are shown against the field.
- **The person is deleted.** They are shown read-only, marked as deleted.
- **It is your own record.** Opening your own record from the list offers the same
  editing as on your profile (see
  [Your account]({{< relref "/docs/user-guide/your-account" >}})), and you cannot
  change your own role.
- **A Scope Admin looking at a co-owner.** A Scope Admin can edit and delete the
  Users of a scope they own, but sees a co-owner's record read-only, because the
  API would refuse the change. A System Admin can update anyone.

## UI-19: Delete a person, logically and permanently

Screen: `/scopes/:scopeId/persons/:personId`, at the bottom of the person's detail.
A System Admin can do both kinds of deletion. A Scope Admin can do the logical one
only, and only for a User.

Logical deletion:

1. Press **Delete person** and confirm in a dialog that names the person.
2. The UI deletes them and returns to the list with a confirmation.

Permanent deletion (System Admin):

1. Press **Delete permanently**.
2. The dialog names the person and says that their record, the applications they
   own, their tokens and their scope membership are all erased. It asks you to type
   their email address before the confirm button works.
3. Confirm. The UI deletes them and returns to the list.

Other things that can happen:

- **You cancel.** Nothing is sent.
- **The API refuses.** For example, the person is the last owner of a scope. Its
  messages are shown and the person stays open.
- **The typed email does not match.** The confirm button stays disabled.
- **It is your own record.** The deletion controls are disabled, and the screen says
  you cannot delete your own account from here.
- **You are a Scope Admin.** You never see the permanent deletion control.

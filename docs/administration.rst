Creating Members
================

Membership records




Security Permissions
====================

There are a number of permissions a user must be given in order to
access various elements of the system. In order to grant/revoke
permissions, the Admin area must be accessed. From there select "Users".

This interface is part of Django's user management interface. Search
for the user you want to modify.

In the "User permissions" area of the "Change user" screen you may
attach/detach a long list of permissions to the user.

The permissions relavant to membership management are:

- coop | member | Can view all member details
- coop | member | Can view limited member details
- coop | member | Can add member
- coop | member | Can change member
- coop | loan | Can change loan
- coop | work | Can change work
- coop | member fee | Can change work



System Level Permissions
------------------------

In addition to the permissions above, to enable a member to be able to
manage lower level controls the following permissions are relevant.

- "Active" controls whether the user is able to login in any way at all.
- "Staff status" allows the user to access and use the lower level admin pages.
- "Superuser status" allows the user full access to everything.
- auth | user | Can change user - lets people change the above settings

Users allowed to login will also need to have their password set.







Creating Members
================

A member who is part of the "Coop Member Manager" system group (see Security Permissions) will find
an "Add Member" option on the main menu.



Security Permissions
====================

There are a number of permissions a user must be given in order to
access various elements of the system. Most permissions are granted
by adding a Member/User to a system group. (Important: do not
confuse the system level groups with the Membership System groups
as seen on the Member details page.)

There are three system level groups available:

- Coop Member Viewer
    - can view member information, but make no changes
    - has access to member search

- Coop Member Manager
    - can make changes to member information
    - "Edit" buttons will be available
    - "Add Member" will be an option on the main menu

- Coop System Manager
    - can make changes to membership system data (such as adding new role and flag types)
    - "Admin" will appear on the main menu

Currently only a "superuser" can add/remove members from the system groups,
via the system "User" admin page.

If you are a superuser you will see an additional link at the bottom of
the "Edit" page for a member. This will take you to their system level User admin page.
On that page, near the bottom, you can add/remove system groups for the user.

Note: in order for any of the above groups to work the Member will need to have
a password and permission to login. The password and login permission can be set
via the regular Member Edit page.

Important: if putting a member in the "Coop System Manager" group, you also need to
check the "is staff" checkbox.

There is a "superuser" flag on the system User admin page. If this is checked then the
user will have full access to everything with no restrictions.

Permission Details
``````````````````

To see/modify what exact permissions are granted to each of the groups above, a superuser
can access the /admin/auth/group/ page and view the attached permissions.





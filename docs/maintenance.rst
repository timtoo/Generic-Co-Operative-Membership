Creating System Admin Users
===========================

When a Member is created, a "User" record is created along with the "Member" record. The User record
contains basic identification and authentication information, such as login and password. Access to
various elements of the membership system are based on roles attached to the Member, but there is an
additional system level "admin" and "superuser" flags on the User record. To access the interface
to toggle these flags you must have login to the /admin interface with a User record having the
"admin" or "superuser" flag.








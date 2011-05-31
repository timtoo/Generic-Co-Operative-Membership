Technical Notes
===============

A collection of technical notes explaining some design decisions, the state of various
subsystems, and also in places documenting future intentions.


Database
--------

Initial Schema/Data Setup
`````````````````````````

A *post_syncdb* signal runs the `setup_all()` function in the `setupdb.py`
model after syncdb is (almost) finished. See doc string at the top of the
`setupdb.py` model for details. This model sets up special requirements for the
postgresql database, and loads initial data.


City / Province / Country
`````````````````````````

It was considered to make the City/Province/Country tables simple fields on the
address record. The complication of normalizing this data is probably not
needed. The Country table is particularly over done. This structure and these
tables were taken from another project, however, and it was hoped they could be
dropped in with minimal effort.

Noramlizing Accents
```````````````````

For the sake of simplified full-text search, triggers are in place for
noramlizing non-ascii text. This means that, for example, French words with
accents can be searched for without accents.

Since this normalization is needed for full text indexing, the same function
has been used in database triggers in the database to provide normalized values
for other fields, such as city names, rather than at the application level.


Design Issues
-------------

Member vs User
``````````````

Currently the "Member" record is a profile attached to a Django user record.
It might be better (for simplicity, security, and portability) to make "Member"
stand alone, and not be attached to the
Django User mechanisms. This would require writing custom authentication
code if allowing Members to log in. Alternately signals could sync redundant
information in the Member records with the Django User records as needed.


Security/Permissions
````````````````````

The eventual plan is to have the permissions attached to membership system "Roles".
For now we are going to use Django's built in "Group" support and add permissions
that way, which may duplicate some membership system roles, and these Groups then
are assigned to individual Members (represented in standard Django User records).

Perhaps an intermediate step (or even an acceptable solution) would be to automate
the syncronization of certain pre-defined Groups with Roles, or the assigning of
Django groups to "Roles" rather than Users.

Groups grant classes of access:

- Superuser: can access anything (Django User setting)
- Staff: can access admin screens (Django User setting)
- Membership Editor: able to edit all aspects of a user record
- Loan Editor: able to add/modify loans
- Credit Editor: able to modify work credits
- System Editor: able to modify roles & group types (may be same as Staff)









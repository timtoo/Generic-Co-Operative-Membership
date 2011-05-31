Karma Co-operate Case Studies
=============================

Following are some notes specifically related to the implementation/operations
for Karma Co-operative.

Member ID
---------

At Karma Co-operative we want the cash register to associate transactions with
a member/group ID. The cash register is limited to digits followed by a letter
to use as identifiers.

For this reason Karma will adopt the convention of using the ID number of a
member's "household" group (which is created for every new member) followed by
a letter for each member's "login" ID.

For for example, if the members are part of group #123 then the first member's
login will be '123'. The second will be '123B', the third will be '123C'. And
so on.

For simplicity, because 75% of members are the only member in their household
group, the first member in the group does not have the letter "A" appended,
though it is implied by the next member having "B" appended.

We may put in support to automatically generate these IDs in the future, but
for now the member login/id has to be manually updated to conform to Karma's
required pattern.

There is the question of whether a member's login should ever be automatically
changed if they change groups. This may cause support problems if we ever have
an interface where users can actually login.




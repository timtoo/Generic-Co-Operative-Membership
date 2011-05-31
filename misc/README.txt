Karma Co-op Membership System
=============================

Originally created for Karma Co-op, this system to manage membership is
intended to be generic and flexible. It is hoped that it may be of use
to other co-operative organizations. It's main features are:

 - Web-based interface for flexible, decentralized management
 - Supports co-operative concepts not found in other organizations
 - Free and open source, allowing full customization
 - Audit trails recording who has made what changes


Major Concepts
==============

The membership system implements the following concepts:

 - Basic member identity and contact info
 - Membership fees
 - Member loans
 - Member work
 - Member roles (such as being on a committee)
 - Member groups (such as households, or any other grouping desired)
 - Member flags: a generic way to identify attributes of members
 - Rewards: members can be awarded credits of various kinds


Setting Up
==========

After installation, the membership system needs to be set up with the
particular elements to be used.

 - Role Types: names of committes, or other organization roles people
   members might have
 - Loan Types: if your organization requires or accepts member loans
 - Group Types: any groupings that may be wanted
 - Member Flags: configure the types of flags members need to have
 - Cities & Provinces/States: set up the most commonly used ones


Technical Requirements
======================

Server Software:
----------------

PostgreSQL
Apache

Python Modules:
---------------

django
unidecode
psycopg2





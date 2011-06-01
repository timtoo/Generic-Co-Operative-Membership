#!python

# Generic Co-operative Membership System.
# Copyright 2011 Tim Middleton
#
# Generic Co-operative Membership System is free software: you can
# redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Generic Co-operative Membership System is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Generic Co-operative Membership System.  If not, see
# <http://www.gnu.org/licenses/>.

"""Since Django methods are setting extra requirements of a database are at
best half baked, we'll have to do it ourselves, somewhat awkwardly. Issues with
Django:

  - can't load anything much more complex than INSERT/UPDATE statements in
    sql/* files
  - not all syncdb extra SQL is executed via test runner

This script loads the arbitrary sql from a seprate file called sql/setupdb.sql
and executes it. It uses sql comments to divide up the SQL and execute it in
blocks, in order to try to isolate problems somewhat.

Currently these functions will be executed using the post_syncdb signal. It
should be noted that Django signals post_syncdb near the end of the syncdb but
not actually after it (as one would expect judging by the name -- yet another
django database setup issue). This could cause complications.

Until a better method is found...
"""
import os
import logging
import re

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from settings import *

from django.db import connection, transaction
from django.db.models import Q
import django.contrib.auth.models

SETUPDB_DONE=False

def load_sql_blocks(filename='setupdb.sql', ignore_checks=False):
    # file should be sql/setupdb.sql
    sql = os.path.abspath(__file__).rsplit(os.sep,1)[0] + os.sep + 'sql' + os.sep + filename
    cursor = connection.cursor()

    blocks = []
    current_block = []
    current_check = ''

    def append_block(blocks, current_check, current_block):
        ok = True
        if current_block:
            if current_check and (not ignore_checks):
                cursor.execute(current_check.replace('%', '%%'))
                if cursor.fetchone():
                    print "INFO: data exists:", current_check
                    ok = False
            if ok:
                blocks.append('\n'.join(current_block))

        return blocks

    if os.path.exists(sql):
        for l in open(sql,'r'):
            l = l.strip()
            if l.startswith('--'):
                append_block(blocks, current_check, current_block)
                if current_block:
                    current_block = []
                    current_check = ''
                m = re.match(r'(?i)--\s*CHECK:\s*(.*)', l)
                if m:
                    current_check = m.group(1)
                m = re.match(r'(?i)--\s*INCLUDE:\s*(.*)', l)
                if m:
                    blocks.extend(load_sql_blocks(m.group(1).strip(), ignore_checks=ignore_checks))
            elif l:
                current_block.append(l)
        append_block(blocks, current_check, current_block)
    else:
        raise RuntimeError, "setupdb: can't read file: %s" % sql

    return blocks

def load_data(model, unique_field, data, seq=True):
    """Load a list of dictionaries into a given model. The unique_field name is checked
    first to make sure it doesn't already exist."""
    changed = False
    for d in data:
        if model.objects.filter(**{unique_field: d[unique_field]}).count() == 0:
            o = model.objects.create(**d)
            o.save()
            changed = True
        else:
            print "INFO: data exists: '%s' in %s" % (d[unique_field], model)

    if changed and seq:
        pk = model._meta.pk.name
        table = model._meta.db_table
        connection.cursor().execute("""
            select setval(pg_get_serial_sequence('%s', '%s'), max(%s)) from %s;
            """ % (table, pk, pk, table))


def load_app_settings(model):
    data = (
        { 'name': 'coop_name',
          'label': 'Co-op Name',
          'value': 'Generic Co-op',
          'data_type': 'S',
          'help_text': 'The full name of the organization'
          },
        { 'name': 'short_coop_name',
          'label': 'Short Co-op Name',
          'value': 'Generic',
          'data_type': 'S',
          'help_text': 'A short version of the co-op\'s name, if any'
          },
    )
    load_data(model, 'name', data, seq=False)


def load_member_flag_type(model):
    data = (
        {
        'member_flag_type_id': 1,
        'member_flag_type_label': 'Working Member',
        'member_flag_type_description': 'The member should be assigned required work hours',
        'member_flag_type_system': True
        },
        {
        'member_flag_type_id': 2,
        'member_flag_type_label': 'Working Exception',
        'member_flag_type_description': 'The member is exempt from working',
        'member_flag_type_system': True
        },
        {
        'member_flag_type_id': 3,
        'member_flag_type_label': 'Loan Refund Requested',
        'member_flag_type_description': 'Member has requested their loan(s) be refunded',
        'member_flag_type_system': True
        },
    )
    load_data(model, 'member_flag_type_id', data)

def load_role_type(model):
    data = (
        {
        'role_type_id': 1,
        'role_type_label': 'Active Member',
        'role_type_description': 'The member is an active member',
        'role_type_active': True,
        'role_type_ts': 'now',
        },
        {
        'role_type_id': 2,
        'role_type_label': 'Board Member',
        'role_type_description': 'The member serves on the board of directors',
        'role_type_active': True,
        'role_type_ts': 'now',
        },
        {
        'role_type_id': 3,
        'role_type_label': 'Officer',
        'role_type_description': 'The member serves as an officer',
        'role_type_active': True,
        'role_type_ts': 'now',
        },
        {
        'role_type_id': 3,
        'role_type_label': 'Committee',
        'role_type_description': 'The member serves on a committee',
        'role_type_active': True,
        'role_type_ts': 'now',
        },
    )
    load_data(model, 'role_type_id', data)

def load_event_types(model):
    data = (
        { 'member_event_type_id': 1,
          'member_event_type_label': 'Note',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 2,
          'member_event_type_label': 'Import Note',
          'member_event_type_active': False,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 3,
          'member_event_type_label': 'Resignation',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 4,
          'member_event_type_label': 'Join',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 5,
          'member_event_type_label': 'Work',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 6,
          'member_event_type_label': 'Loan',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 7,
          'member_event_type_label': 'Update',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
        { 'member_event_type_id': 8,
          'member_event_type_label': 'Fee',
          'member_event_type_active': True,
          'member_event_type_ts': 'now',
          },
    )
    load_data(model, 'member_event_type_id', data)

def load_loan_types(model):
    data = (
        { 'loan_type_id': 1,
          'loan_name': 'Member Loan',
          'loan_description': 'Optional Member Loan',
          'loan_amount_default': '0.00',
          'loan_type_active': True,
          'loan_required': False,
          'loan_interest_rate': '0.00',
          'loan_type_ts': 'now',
          'loan_type_update_ts': 'now',
          },
    )
    load_data(model, 'loan_type_id', data)

def load_work_types(model):
    data = (
        { 'work_type_id': 1,
          'work_name': 'Assigned Hours',
          'work_description': 'Hours assigned that the member must fullfill',
          'work_amount_default': '0.00',
          'work_type_active': True,
          'work_type_ts': 'now',
          'work_requisition': True,
          'work_type_update_ts': 'now',
          },
        { 'work_type_id': 2,
          'work_name': 'Fullfilled Hours',
          'work_description': 'Hours the member has worked to fullfill requirements',
          'work_amount_default': '0.00',
          'work_type_active': True,
          'work_requisition': False,
          'work_type_ts': 'now',
          'work_type_update_ts': 'now',
          },
        { 'work_type_id': 3,
          'work_name': 'Volunteer Hours',
          'work_description': 'Hours worked on a volunteer basis',
          'work_amount_default': '0.00',
          'work_type_active': True,
          'work_requisition': False,
          'work_type_ts': 'now',
          'work_type_update_ts': 'now',
          },
        { 'work_type_id': 4,
          'work_name': 'Compensated Hours',
          'work_description': 'Hours worked for compenstation (probably store credit)',
          'work_amount_default': '0.00',
          'work_type_active': True,
          'work_requisition': False,
          'work_type_ts': 'now',
          'work_type_update_ts': 'now',
          },
    )
    load_data(model, 'work_type_id', data)

def load_work_activities(model):
    data = (
        { 'work_activity_id': 1,
          'activity_name': 'General',
          'activity_description': 'General work not otherwise specified.',
          'work_activity_active': True,
          'work_activity_ts': 'now',
          'work_activity_update_ts': 'now',
          },
    )
    load_data(model, 'work_activity_id', data)

def load_reward_types(model):
    data = ()
    load_data(model, 'reward_id', data)

def load_work_activity(model):
    data = (
        { 'work_activity_id': 1,
          'activity_name': 'Generic',
          'activity_description': 'Any work activity not otherwise clasified',
          'work_activity_active': True,
          'work_activity_ts': 'now',
          'work_update_activity_ts': 'now',
          },
    )
    load_data(model, 'work_activity_id', data)

def load_fee_type(model):
    data = (
        { 'fee_type_id': 1,
          'fee_type_name': 'Generic',
          'fee_type_description': 'Unspecified fee',
          'fee_type_active': True,
          'fee_type_ts': 'now',
          'fee_type_update_ts': 'now',
          'fee_recurring': 1,
          'fee_amount_default': '0.0',
          },
    )
    load_data(model, 'fee_type_id', data)

def setup_auth():
    print "Setting up permissions..."

    # create groups
    groups = {
            'Coop System Manager': None,
            'Coop Member Manager': None,
            'Coop Member Viewer': None
            }
    for g in groups.keys():
        groups[g], created = django.contrib.auth.models.Group.objects.get_or_create(name=g)
        if created:
            print "Created group: %s..." % g
            groups[g].save()

    # System Manager (add create/modify to the following tables)
    add_change_models = ('city', 'appsettings', 'commtype', 'country',
            'feetype', 'loantype', 'membereventtype', 'memberflagtype',
            'resignationreasonlist', 'rewardtype', 'roletype',
            'workactivity', 'worktype')

    for ac in add_change_models:
        for p in django.contrib.auth.models.Permission.objects.filter(
                Q(codename__startswith='add_') | Q(codename__startswith='change_'),
                content_type__app_label='coop', content_type__model=ac):
            groups['Coop System Manager'].permissions.add(p.id)

    # Member Manager (add change_member -- used by coop app for many permissions)
    p = django.contrib.auth.models.Permission.objects.get(codename='change_member',
                content_type__app_label='coop', content_type__model='member')
    groups['Coop Member Manager'].permissions.add(p.id)


    # Member Viewer
    p = django.contrib.auth.models.Permission.objects.get(codename='view',
                content_type__app_label='coop', content_type__model='member')
    groups['Coop Member Viewer'].permissions.add(p.id)


def setup_all(sender, **kw):

    # hack due to signal called multiple times:
    # https://github.com/dcramer/django-sentry/issues/100
    global SETUPDB_DONE
    if SETUPDB_DONE:
        return None
    SETUPDB_DONE=True

    if sender.__name__ == 'coop.models':
        blocks = load_sql_blocks(ignore_checks=kw.get('ignore_checks'))
        cursor = connection.cursor()
        for sql in blocks:
            try:
                if kw.get('print_only'):
                    print sql,'\n'
                else:
                    cursor.execute(sql)
            except:
                print "Problem with SQL:\n%s" % sql
                raise

        load_app_settings(sender.AppSettings)
        load_member_flag_type(sender.MemberFlagType)
        load_event_types(sender.MemberEventType)
        load_role_type(sender.RoleType)
        load_fee_type(sender.FeeType)
        load_work_types(sender.WorkType)
        load_work_activities(sender.WorkActivity)
        load_reward_types(sender.WorkType)
        load_loan_types(sender.LoanType)
        setup_auth()

        transaction.commit_unless_managed()


if __name__ == '__main__':
    import coop.models
    #setup_all(coop.models)
    setup_all(coop.models, print_only=True)
    #setup_all(coop.models, print_only=True, ignore_checks=True)



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

"""Support functions for views.py

(Try to keep views.py for just functions that return HTML, to more
cleanly be able to manage permissions/security there.)
"""
from django.db import connection, transaction
from django.db import models

import coop.models
import coop.util

def stats():
    """Gather various statistics for display on the main page"""

    data = {}

    data['status'] = coop.models.Member.objects.values(
        'member_status', 'member_status__member_status_label').annotate(
        count=models.Count('member_status')).order_by(
        'member_status__member_status_label')

    data['new_members'] = [ str(x['count']) for x in tuple(coop.util.queryDict("""
            select cast(date_trunc('month',member_ts) as date) AS "date",
                count(date_trunc('month',member_ts)) AS "count"
                from coop_member group by date_trunc('month',member_ts)
                order by date_trunc('month',member_ts)
            """))[-18:] ]
    data['new_members_list'] = ','.join(data['new_members'])
    if len(data['new_members'])>0:
        data['new_members_this_month'] = data['new_members'][-1]
    if len(data['new_members'])>1:
        data['new_members_last_month'] = data['new_members'][-2]

    return data

def logEvent(request, event_type_id, member, detail):
    coop.models.MemberEvent.objects.create(
            event_type_id=event_type_id,
            member_event_detail=detail,
            member_id=member,
            added_by=request.user,
            )




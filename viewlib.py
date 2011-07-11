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

    data['new_member_summary'] =  tuple(coop.util.queryDict("""
            select cast(date_trunc('month',member_ts) as date) AS "date",
                count(date_trunc('month',member_ts)) AS "count",
                max(member_ts) AS "latest",
                min(member_ts) AS "newest"
                from coop_member group by date_trunc('month',member_ts)
                order by date_trunc('month',member_ts) DESC
                LIMIT 18
            """))
    data['new_members_list'] = ','.join(reversed([str(x['count']) for x in data['new_member_summary']]))
    if len(data['new_member_summary'])>0:
        data['new_members_this_month'] = data['new_member_summary'][0]['count']
        data['newest_member_date'] = data['new_member_summary'][0]['latest']
    if len(data['new_member_summary'])>1:
        data['new_members_last_month'] = data['new_member_summary'][1]['count']

    return data

def logEvent(request, event_type_id, member, detail):
    coop.models.MemberEvent.objects.create(
            event_type_id=event_type_id,
            member_event_detail=detail,
            member_id=member,
            added_by=request.user,
            )




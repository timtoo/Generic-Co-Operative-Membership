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

import django.dispatch

# hook to customize behavior for viewing members
pre_member_view = django.dispatch.Signal(providing_args=['request', 'data'])
pre_member_add_form = django.dispatch.Signal(providing_args=['request', 'user', 'address', 'optional'])
post_member_add_save = django.dispatch.Signal(providing_args=['request', 'user', 'member', 'address', 'optional'])



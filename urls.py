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

from django.conf.urls.defaults import *
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.views import login

urlpatterns = patterns('coop.views',
    ('^member/add', 'member_add'),
    ('^member/group/random', 'random_group'),
    ('^member/group/(?P<member_group_id>\d+)', 'member_group_view'),
    ('^member/random', 'random_member'),
    ('^member/search', 'member_search'),
    ('^member/(?P<member_id>\d+)/edit', 'member_edit'),
    ('^member/(?P<member_id>\d+)', 'member_view'),
    ('^member/update', 'member_update'),
    ('^test', 'test'),
    ('^member', 'member_view'),
    ('^logout', 'logout_view'),
    url('^$', 'default', name="home"),
)

urlpatterns += patterns('',
    ('^login', 'django.contrib.auth.views.login'),
)



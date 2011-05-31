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

from django import template

from coop.appsettings import AppSettings

register = template.Library()

class StringNode(template.Node):
    """Wrap a string in a Note object"""
    def __init__(self, value):
        self.value = value

    def render(self, context):
        return str(self.value)

@register.tag(name="setting_value")
def get_setting_value(parser, token):
    tag, key = token.split_contents()
    return StringNode(AppSettings.get(key))



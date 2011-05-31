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

"""A table and special manager for storing application settings.

This really should be genericized into a separate re-usable app.
"""

from django.db import models

class AppSettingsManager(models.Manager):
    cached = {}

    def __call__(self, key, default=None):
        """Allow access to settings by using object attribute name"""
        try:
            if not self.cached.has_key(key):
                d = self.get(name=key)
                if d.data_type == 'I':
                    self.cached[key] = int(d.value or 0)
                else:
                    self.cached[key] = d.value or ''

        except AppSettings.DoesNotExist:
            pass

        return self.cached.get(key, default)


class AppSettings(models.Model):
    name = models.CharField(max_length=32, primary_key=True,
            help_text="Key name to refer to this setting")
    label = models.CharField(max_length=64, unique=True,
            help_text="Human readable label for this setting")
    value = models.CharField(max_length=255,
            help_text="Value for setting")
    data_type = models.CharField(max_length=1, default="S",
            help_text="Data type to convert setting to")
    help_text = models.CharField(max_length=255,
            help_text="Extra info/instructions for this setting")

    objects = models.Manager()
    get = AppSettingsManager()

    class Meta:
        verbose_name_plural = 'App Settings'
        ordering = ('name', 'label')

    def __unicode__(self):
        return u'AppSettings: %s (%s): %s' % (self.name, self.label, self.value)

    def save(self, *args, **kwargs):
        AppSettings.get.cached[self.name] = self.value # update cached manager
        super(AppSettings, self).save(*args, **kwargs)


def context_processor(request):
    class get_setting_value(object):
        def __getattr__(self, key):
            return AppSettings.get(key)

    return {
        'settings': get_setting_value(),
    }



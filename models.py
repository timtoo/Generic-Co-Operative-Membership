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

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_syncdb
from django.dispatch import receiver


from coop.appsettings import AppSettings

# --------------------------------------------------------------
# Fields
# --------------------------------------------------------------


class VectorField (models.Field):
    """Allow models to have a "tsvector" field"""

    def __init__( self, *args, **kwargs ):
        kwargs['null'] = True
        kwargs['editable'] = False
        kwargs['serialize'] = False
        super( VectorField, self ).__init__( *args, **kwargs )

    def db_type( self, connection ):
        return 'tsvector'

# --------------------------------------------------------------
# Managers
# --------------------------------------------------------------

class FeeManager(models.Manager):
    def for_member(self, member_id):
        """Return dict with the following keys:

            count, amount, oldest, newest,
            not_paid_count, not_paid_amount
            oldest_not_paid, newest_not_paid

        """
        data = {}
        data.update(self.filter(models.Q(member=member_id)
                ).aggregate(
                    loaned=models.Sum('fee_amount'),
                    newest=models.Min('fee_ts'),
                    oldest=models.Max('fee_ts'),
                    count=models.Count('fee_amount'),
                ))
        data.update(self.filter(models.Q(member=member_id),
                    fee_paid_ts__isnull=True
                ).aggregate(
                    not_paid_amount=models.Sum('fee_amount'),
                    oldest_not_paid=models.Min('fee_ts'),
                    newest_not_paid=models.Max('fee_ts'),
                    not_paid_count=models.Count('fee_amount'),
                ))
        return data


class LoanManager(models.Manager):
    def for_member(self, member_id):
        """Return dict with the following keys:

            count, amount, oldest, newest,
            not_received_count, not_received_amount
            oldest_not_received, newest_not_received

        """
        data = {}
        data.update(self.filter(models.Q(member=member_id)
                ).aggregate(
                    amount=models.Sum('loan_amount'),
                    newest=models.Min('loan_ts'),
                    oldest=models.Max('loan_ts'),
                    count=models.Count('loan_amount'),
                ))
        data.update(self.filter(models.Q(member=member_id),
                    loan_received_ts__isnull=True,
                    loan_withdrawn_ts__isnull=False
                ).aggregate(
                    not_recieved_amount=models.Sum('loan_amount'),
                    oldest_not_received=models.Min('loan_ts'),
                    newest_not_received=models.Max('loan_ts'),
                    not_received_count=models.Count('loan_amount'),
                ))
        return data


class WorkManager(models.Manager):
    """Provides methods for easy lookup of different work types, and also
    a summary of work owed/done.
    """
    def assigned(self):
        return self.filter(models.Q(work_type=1))

    def fulfilled(self):
        return self.filter(models.Q(work_type=2))

    def volunteer(self):
        return self.filter(models.Q(work_type=3))

    def for_member(self, member_id):
        """Return dictionary with the following keys:

            assigned_hours, assigned_first, assigned_last, assigned_count,
            fulfilled_hours, fulfilled_first, fulfilled_last, fulfilled_count,
            owed
        """

        hours = self.assigned().filter(member=member_id
                ).aggregate(
                    assigned_hours=models.Sum('work_hours'),
                    assigned_first=models.Min('work_ts'),
                    assigned_last=models.Max('work_ts'),
                    assigned_count=models.Count('work_hours'),
                )
        done = self.fulfilled().filter(member=member_id
                ).aggregate(
                    fulfilled_hours=models.Sum('work_hours'),
                    fulfilled_first=models.Min('work_ts'),
                    fulfilled_last=models.Max('work_ts'),
                    fulfilled_count=models.Count('work_hours'),
                )

        hours.update(done)
        for k in ('assigned_hours', 'fulfilled_hours'):
            if hours[k] is None:
                hours[k] = 0

        hours['owed'] = hours['assigned_hours'] - hours['fulfilled_hours']
        return hours

# -------------------------------------------------------------------
# Location models
# -------------------------------------------------------------------


class Country(models.Model):
    """This schema is adapted from geonames.org;
    it is intended to be populated with data from that site.
    """

    alpha2 = models.CharField(max_length=2, primary_key=True)
    alpha3 = models.CharField(max_length=3, unique=True)
    numeric_code = models.IntegerField(unique=True)
    fips = models.CharField(max_length=250)
    country_name = models.CharField(max_length=250)
    capital = models.CharField(max_length=250, null=True)
    area = models.FloatField(max_length=250, null=True)
    population = models.BigIntegerField()
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=8)
    currency_code = models.CharField(max_length=8)
    currency_name = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    postal_code_format = models.CharField(max_length=250)
    postal_code_regex = models.CharField(max_length=250)
    languages = models.CharField(max_length=250)
    geonameid = models.CharField(max_length=250)
    neighbours = models.CharField(max_length=250)
    equiv_fips = models.CharField(max_length=252)
    alpha2_year = models.IntegerField(null=True)
    alpha2_note = models.TextField(null=True)
    country_norm = models.CharField(max_length=250, verbose_name="Normalized country name")

    class Meta:
        db_table = 'country'
        ordering = ('country_norm',)
        verbose_name_plural = 'Countries'

    def __unicode__(self):
        return u'%s (%s)' % (self.alpha2, self.country_name)

class Province(models.Model):

    province_id = models.IntegerField(primary_key = True, help_text="geonames.org ID")
    province_name = models.CharField(max_length=250)
    province_norm = models.CharField(max_length=250, verbose_name="Normalized province name")
    province_code = models.CharField(max_length=8, help_text="Two character postal province code")
    prcode = models.IntegerField(help_text="Statistics Canada code")
    admin1 = models.CharField(max_length=5, help_text="geonames.org admin1 code")
    country = models.ForeignKey('Country', related_name='provinces',
            db_column='country_id', to_field='numeric_code')

    class Meta:
        db_table = 'province'
        ordering = ('country', 'province_code', 'province_norm',)

    def __unicode__(self):
        return u'%s (%s) country=%s' % (self.province_code, self.province_name, self.country_id)

class City(models.Model):

    city_id = models.AutoField(primary_key = True, editable=False)
    city_name = models.CharField(max_length=250)
    city_norm = models.CharField(max_length=250, verbose_name="Normalized city name")
    province = models.ForeignKey('Province', db_column='province_id',
            related_name='cities', to_field='province_id')

    class Meta:
        db_table = 'city'
        ordering = ('city_norm',)
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return u'%s, province=%s' % (self.city_name, self.province_id)


class Address(models.Model):

    address_id = models.AutoField(primary_key = True, editable=False)
    address_active = models.BooleanField(default=True)
    member = models.ForeignKey('Member', db_column='member_id',
            related_name='addresses', to_field='member_id')
    address_line1 = models.CharField(max_length=250, verbose_name="Street address", blank=True)
    address_line2 = models.CharField(max_length=250, verbose_name="Address line 2", blank=True)
    postal_code = models.CharField(max_length=8, blank=True)
    city = models.ForeignKey('City', db_column='city_id',
            related_name='addresses', to_field='city_id', db_index=True)
    address_ts = models.DateTimeField(editable=False, auto_now_add=True)
    address_update_ts = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('-address_active','-address_id')

    def __unicode__(self):
        return u'%s: %s %s %s' % (self.address_id, self.address_line1,
                self.address_line2, self.postal_code)

    def address_line(self):
        out = []
        if self.address_line1:
            out.append(self.address_line1)
        if self.address_line2:
            out.append(self.address_line2)
        out.append((self.city.city_name + ' ' + self.city.province.province_code).strip())
        if self.postal_code:
            out[-1] += '  ' + self.postal_code
        return ', '.join(out)

    def address_text(self):
        out = ''
        if self.address_line1:
            out += self.address_line1 + '\n'
        if self.address_line2:
            out += self.address_line2 + '\n'
        out += self.city.city_name + ' '
        out += self.city.province.province_code + '  '
        if self.postal_code:
            out += self.postal_code
        return out.strip()

    def address_html(self):
        return self.address_text().replace('\n', '<br>').replace('&', '&amp;').replace('  ', '&nbsp; ')


# ---------------------------------------------------------
# "Type" models
# ---------------------------------------------------------

class CommType(models.Model):
    comm_type_id = models.AutoField(primary_key = True)
    comm_type_label = models.CharField(max_length=32, unique=True)
    comm_type_active = models.BooleanField(default=True)
    comm_type_priority = models.IntegerField(default=5)
    comm_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    comm_type_url_pattern = models.CharField(max_length=250)

    class Meta:
        ordering = ('-comm_type_active', 'comm_type_priority', 'comm_type_label')

    def __unicode__(self):
        return self.comm_type_label


class LoanType(models.Model):
    members = models.ManyToManyField('Member', through='Loan')
    loan_type_id = models.AutoField(primary_key=True)
    loan_name = models.CharField(max_length=250, unique=True)
    loan_description = models.TextField(default='', blank=True)
    loan_amount_default = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    loan_type_active = models.BooleanField(default=True)
    loan_required = models.BooleanField(default=False)
    loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    loan_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    loan_type_update_ts = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return self.loan_name


class MemberEventType(models.Model):
    members = models.ManyToManyField('Member', through='MemberEvent')
    member_event_type_id = models.IntegerField(primary_key = True, editable=False)
    member_event_type_label = models.CharField(max_length=32, unique=True)
    member_event_type_active = models.BooleanField(default=True)
    member_event_type_ts = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        ordering = ('member_event_type_label','member_event_type_id')

    def __unicode__(self):
        return self.member_event_type_label


class MemberFlagType(models.Model):
    members = models.ManyToManyField('Member', through='MemberFlag')
    member_flag_type_id = models.AutoField(primary_key = True)
    member_flag_type_label = models.CharField(max_length=32, unique=True)
    member_flag_type_description = models.TextField()
    member_flag_type_active = models.BooleanField(
            help_text="Flag type is available for use?")
    member_flag_type_has_detail = models.BooleanField(
            help_text="This flag is expected to have data associated with it.")
    member_flag_detail_options = models.CharField(max_length=255,
            help_text="Pipe-separated options to restrict the detail to.")
    member_flag_type_system = models.BooleanField(default=False, editable=False,
            help_text="This flag is required by the system - do not delete")
    member_flag_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    work_type = models.ForeignKey('WorkType', null=True,
            db_column='work_type_id', to_field='work_type_id',
            help_text='Work type to automatically be assigned to members with this flag')
    reward_type = models.ForeignKey('RewardType', null=True,
            db_column='reward_type_id', to_field='reward_type_id',
            help_text='Reward to automatically be applied to members with this flag')
    fee_type = models.ForeignKey('FeeType', null=True,
            db_column='fee_type_id', to_field='fee_type_id',
            help_text='Fee to be applied to members with this flag')

    class Meta:
        ordering = ('-member_flag_type_active', 'member_flag_type_label')

    def __unicode__(self):
        return self.member_flag_type_label


class MemberGroupType(models.Model):

    member_group_type_id = models.AutoField(primary_key = True)
    member_group_type_label = models.CharField(max_length=250)
    member_group_type_description = models.TextField()
    member_group_type_active = models.BooleanField(default=True,
            help_text="This group type is available and in use")
    member_group_type_auto_create = models.BooleanField(default=False,
            help_text="A new group of this group type is created for each new member")
    member_group_type_unique = models.BooleanField(default=True,
            help_text="Members can only belong to one group of this type at a time.")
    member_group_type_share_hours = models.BooleanField(default=False,
            help_text="Members of this group pool their required work hours.")
    member_group_type_ts = models.DateTimeField(editable=False, auto_now_add=True,
            help_text="When this group type was created")

    def __unicode__(self):
        return u'MemberGroupType id=%s name=%s active=%s' % (
                self.member_group_type_id, self.member_group_type_label,
                self.member_group_type_active)


class FeeType(models.Model):
    fee_type_id = models.AutoField(primary_key=True)
    fee_type_name = models.CharField(max_length=250, unique=True)
    fee_type_description = models.TextField(default='', blank=True)
    fee_recurring = models.IntegerField(choices=((1, 'One-time'),
            (3, 'Monthly'), (4, 'Quarterly'), (2, 'Bi-annually'),
            (5, 'Annual')),
            default=1)
    # month number, or 0 for aniversary based on member_ts
    fee_recurring_start =  models.IntegerField(choices=(
            (0, 'Joined Date'), (1, 'January'), (2, 'February'), (3, 'March'),
            (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'),
            (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'),
            (12, 'December')), null=True, blank=True,
            help_text='Date recurring fee is based at.')
    fee_amount_default = models.DecimalField(max_digits=9, decimal_places=2,
            default=0.0, help_text="Default fee amount")
    fee_type_active = models.BooleanField(default=True)
    fee_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    fee_type_update_ts = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        ordering = ('fee_type_name',)

    def __unicode__(self):
        return self.fee_type_name


class RewardType(models.Model):
    reward_type_id = models.AutoField(primary_key=True)
    reward_name = models.CharField(max_length=250, unique=True)
    reward_description = models.TextField(default='', blank=True)
    reward_amount = models.DecimalField(max_digits=9, decimal_places=2,
            default=0.0, help_text="Default hours for this reward type")
    reward_type_active = models.BooleanField(default=True)
    reward_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    reward_type_update_ts = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return self.reward_name


class RoleType(models.Model):

    members = models.ManyToManyField('Member', through='Role')
    role_type_id = models.AutoField(primary_key = True)
    role_type_label = models.CharField(max_length=250, unique=True)
    role_type_description = models.TextField()
    role_type_active = models.BooleanField()
    role_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    work_type = models.ForeignKey('WorkType', null=True,
            db_column='work_type_id', to_field='work_type_id',
            help_text='Work type to automatically be assigned to members with this role')
    reward_type = models.ForeignKey('RewardType', null=True,
            db_column='reward_type_id', to_field='reward_type_id',
            help_text='Reward to automatically be applied to members with this role type')
    fee_type = models.ForeignKey('FeeType', null=True,
            db_column='fee_type_id', to_field='fee_type_id',
            help_text='Fee to be applied to members with this role type')

    def __unicode__(self):
        return self.role_type_label


class WorkType(models.Model):
    members = models.ManyToManyField('Member', through='Work')
    work_type_id = models.AutoField(primary_key=True)
    work_name = models.CharField(max_length=250, unique=True)
    work_description = models.TextField(default='', blank=True)
    work_amount_default = models.DecimalField(max_digits=9, decimal_places=2,
            default=0.0, help_text="Default monthly hours for this work type")
    work_type_active = models.BooleanField(default=True)
    work_requisition = models.BooleanField(help_text="This work type is a request for a member to do work")
    work_type_ts = models.DateTimeField(editable=False, auto_now_add=True)
    work_type_update_ts = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        ordering = ('work_requisition', 'work_name',)

    def __unicode__(self):
        return (self.work_requisition and u'*' or u'') + self.work_name


# -----------------------------------------------------------
# Member
# -----------------------------------------------------------

class Member(models.Model):

    member_id = models.AutoField(primary_key=True, editable=False)
    member_phone = models.CharField(max_length=50, verbose_name="Phone", default='', blank=True)
    email_status = models.CharField(max_length=1, default='V',
            verbose_name="Email status", choices=(
            ('V', 'Valid'), ('I', 'Invalid'), ('N', 'Do Not Email')))
    member_status = models.ForeignKey('MemberStatus', db_column='member_status_id',
            to_field='member_status_id', related_name='members')
    member_ts = models.DateTimeField(editable=False, auto_now_add=True)
    member_resigned_date = models.DateField(null=True)
    member_update_ts = models.DateTimeField(editable=False, auto_now=True)
    member_last_activity_ts = models.DateTimeField(null=True,
            help_text="The last time this member was known to be active with the co-op")
    # ForeignKey rather than OneToOneField because of null issue and unable to trap DoesNotExist.
    # see: https://code.djangoproject.com/ticket/10227
    user = models.ForeignKey(User, to_field='id',
            related_name='member', db_column="django_user_id",
            help_text="Links record to a django User",
            verbose_name="Username")

    class Meta:
        permissions = (
                ('limited', 'Can view limited member details'),
                ('view', 'Can view all member details'),
        )
        ordering = ('member_id',)

    def __unicode__(self):
        return u'%s' % (self.member_id,)

    def get_work_summary(self):
        return Work.objects.for_member(self.member_id)

    def get_fee_summary(self):
        return Fee.objects.for_member(self.member_id)

    def get_loan_summary(self):
        return Loan.objects.for_member(self.member_id)

    def get_full_name(self):
        return ' '.join([x for x in (self.user.first_name, self.user.last_name) if x])

    def get_full_name_reverse(self):
        return ', '.join([x for x in (self.user.last_name, self.user.first_name) if x])


class MemberFts(models.Model):
    member = models.ForeignKey('Member', primary_key=True, editable=False,
            related_name="fts", db_column="member_id")
    member_text = models.TextField(editable=False)
    member_fts = VectorField(editable=False)
    member_fts_ts = models.DateTimeField(editable=False)

    def __unicode__(self):
        return u'%s' % self.member_id

class MemberStatus(models.Model):

    member_status_id = models.IntegerField(primary_key=True)
    member_status_label = models.CharField(max_length = 16, unique=True)

    def __unicode__(self):
        return u'%s: %s' % (self.member_status_id, self.member_status_label)


class ResignationReasonList(models.Model):
    resignation_reason_id = models.AutoField(primary_key = True)
    resignation_reason_text = models.CharField(max_length=254, unique=True)
    resignation_reason_active = models.BooleanField(default = True)
    resignation_reason_ts = models.DateTimeField(editable=False, auto_now_add=True,
            help_text="When this resason was created")

    def __unicode__(self):
        return u'%s' % (self.resignation_reason_text,)

class MemberGroupMember(models.Model):
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='groups', db_index=True)
    member_group = models.ForeignKey('MemberGroup', db_column='member_group_id',
            to_field='member_group_id', related_name='group_members', db_index=True)
    member_group_member_ts = models.DateTimeField(editable=False, auto_now_add=True,
            help_text="When this member was added to this group")
    member_group_rep = models.BooleanField(default=False,
            help_text="Member is the/a representative for this group")

    class Meta:
        unique_together = (('member_group', 'member'),)

    def __unicode__(self):
        return u'member=%s member_group=%s' % (self.member, self.member_group)

class MemberGroup(models.Model):

    members = models.ManyToManyField('Member', through='MemberGroupMember')
    member_group_id = models.AutoField(primary_key=True)
    member_group_name = models.CharField(max_length=80, blank=True)
    member_group_type = models.ForeignKey('MemberGroupType',
            db_column='member_group_type_id',
            to_field='member_group_type_id',
            db_index=True)
    member_group_ts = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        return u'%s: %s' % (self.member_group_id, self.member_group_name)

    def save(self, *args, **kw):
        """Generate a name if one isn't given"""
        super(MemberGroup, self).save(*args, **kw)
        if not self.member_group_name:
            self.member_group_name = '%s #%s' % (MemberGroupType.objects.get(
                        pk=self.member_group_type_id).member_group_type_label,
                   self.member_group_id)
        super(MemberGroup, self).save(*args, **kw)


class Role(models.Model):
    member = models.ForeignKey('Member', db_column='member_id',
            to_field="member_id", related_name='roles', db_index=True)
    role_type = models.ForeignKey('RoleType', db_column='role_type_id',
            to_field='role_type_id')
    role_start_dt = models.DateField(default=datetime.today,
            help_text="The date the member commences this role")
    role_end_dt = models.DateTimeField(null=True,
            help_text="The date the role for this member completed")
    role_detail = models.CharField(max_length=64, blank=True,
            help_text="A specific/special title/designation for this role")
    role_note = models.TextField(blank=True,
            help_text="Administrative notes regarding this member's activity in this role")
    role_ts = models.DateTimeField(editable=False, auto_now_add=True)


class MemberFlag(models.Model):

    member_flag_id = models.AutoField(primary_key = True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='flags', db_index=True)
    flag_type = models.ForeignKey('MemberFlagType',
            db_column='member_flag_type_id',
            to_field='member_flag_type_id')
    member_flag_detail = models.CharField(max_length=250, null=True)
    member_flag_ts = models.DateTimeField(editable=False, auto_now_add=True)


class MemberEvent(models.Model):
    member_event_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='events')
    event_type = models.ForeignKey('MemberEventType',
            db_column='member_event_type_id',
            to_field='member_event_type_id',
            db_index=True)
    member_event_detail = models.TextField()
    member_event_ts = models.DateTimeField(editable=False, auto_now_add=True)
    added_by = models.ForeignKey(User,
            db_column='added_by',
            to_field='id',
            null=True)

    class Meta:
        ordering = ('-member_event_ts', '-member_event_id')


class MemberComm(models.Model):
    comm_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='commlinks', db_index=True)
    comm_type_id = models.ForeignKey('CommType',
            db_column='comm_type_id',
            to_field='comm_type_id')
    comm_identifier = models.CharField(max_length=250, help_text="email address, phone number, etc")
    comm_identifier_status = models.IntegerField(default=1, choices=(
            (0, 'Inactive'), (1, 'Primary'), (2, 'Secondary')))
    comm_ts = models.DateTimeField(editable=False, auto_now_add=True)


class Fee(models.Model):
    fee_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='fees', db_index=True)
    fee_type = models.ForeignKey('FeeType',
            db_column='fee_type_id',
            to_field='fee_type_id')
    fee_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    fee_note = models.CharField(max_length=250, default='', blank=True)
    fee_ts = models.DateTimeField(editable=False, auto_now_add=True)
    fee_paid_ts = models.DateTimeField(editable=False, null=True, db_index=True)

    objects = FeeManager()

    class Meta:
        ordering = ('-fee_id',)

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='loans', db_index=True)
    loan_type = models.ForeignKey('LoanType',
            db_column='loan_type_id',
            to_field='loan_type_id')
    loan_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.0,
            help_text="The amount to be loaned to the coop.")
    loan_ts = models.DateTimeField(editable=False, auto_now_add=True,
            help_text="When the loan record is created")
    loan_received_ts = models.DateTimeField(editable=False, null=True,
            help_text="The date on which the money for the loan was recieved")
    loan_withdrawn_ts = models.DateTimeField(editable=False, null=True,
            help_text="The date on which the money for the loan was withdrawn")

    objects = LoanManager()

    class Meta:
        ordering = ('-loan_id',)

class Work(models.Model):
    work_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', db_column='member_id',
            to_field='member_id', related_name='work',
            db_index=True)
    work_type = models.ForeignKey('WorkType',
            db_column='work_type_id',
            to_field='work_type_id',
            db_index=True,
            verbose_name="Work type")
    work_activity = models.ForeignKey('WorkActivity',
            db_column='work_activity_id',
            to_field='work_activity_id',
            default = 1,
            db_index=True,
            verbose_name="Activity")
    work_hours = models.DecimalField(max_digits=9, decimal_places=2, default=0.0,
            verbose_name="Hours", help_text="Hours can include decimals.")
    work_note = models.CharField(max_length=250, null=True, blank=True,
            verbose_name="Note")
    work_start_ts = models.DateTimeField(default=datetime.now,
            verbose_name="Start time")
    work_ts = models.DateTimeField(editable=False, auto_now_add=True)

    objects = WorkManager()

    class Meta:
        ordering = ('-work_id',)


class WorkActivity(models.Model):
    members = models.ManyToManyField('Member', through='Work')
    work_activity_id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=250, unique=True)
    activity_description = models.TextField(default='', blank=True)
    work_activity_active = models.BooleanField(default=True)
    work_activity_ts = models.DateTimeField(editable=False, auto_now_add=True)
    work_activity_update_ts = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Work Activities'
        ordering = ('activity_name',)

    def __unicode__(self):
        return self.activity_name



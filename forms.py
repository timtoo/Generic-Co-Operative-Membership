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

from django import forms
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User

import coop.models

class CityModelChoiceField(forms.ModelChoiceField):
    to_field_name = 'city_id'
    qs = coop.models.City.objects.select_related(
                'province', 'province__country').extra(select={'label':
                "city_name || ', ' || province.province_code || ', ' || alpha2"},
                ).order_by('province__country','city_name')
    def label_from_instance(self, obj):
        return obj.label

class BasicAddressForm(forms.ModelForm):
    # this won't scale if there are a large number of cities

#    city = forms.TypedChoiceField(choices = [ ('', '-----') ] + [
#                (x['city_id'], x['label']) for \
#                x in coop.models.City.objects.extra(select={'label':
#                        "city_name || ', ' || province_code || ', ' || alpha2"},
#                        ).filter('city_active'=True).values('city_id', 'label').order_by(
#                        'province__country','city_name') ],
#                coerce=int, required=False, empty_value='')

    #city = CityModelChoiceField(queryset=coop.models.City.objects.extra(select={'label':
    #                    "city_name || ', ' || province_code || ', ' || alpha2"},
    #                    ).order_by('province__country','city_name'))

    city = CityModelChoiceField(queryset=CityModelChoiceField.qs, required=False)

    class Meta:
        model = coop.models.Address
        exclude = ('member', 'address_active')

##    def clean_city(self):
##        return self.cleaned_data['city']

    def clean(self):
        if (self.cleaned_data['address_line1'] or \
                self.cleaned_data['address_line2'] or \
                self.cleaned_data['postal_code']) and \
                not self.cleaned_data['city']:
            raise forms.ValidationError("City must be specified.")
        return self.cleaned_data

    def has_data(self):
        return hasattr(self, 'cleaned_data') and (
                self.cleaned_data['address_line1'] or \
                self.cleaned_data['address_line2'] or \
                self.cleaned_data['postal_code'] or \
                self.cleaned_data['city'])


class AddressForm(BasicAddressForm):
    class Meta:
        model = coop.models.Address
        widgets = { 'member': forms.HiddenInput() }


AddressFormSet = modelformset_factory(coop.models.Address, form=AddressForm)

class BasicMemberForm(forms.ModelForm):
    class Meta:
        model = coop.models.Member
        fields = ('member_phone',)


class AddMemberForm(forms.ModelForm):
    """Form for creating new members.

    Basic User information, plus some Member fields.

    This is unfortunately a redundant mishmash of fields from three different tables
    """
    # override username to get rid of help_text and set required=False
    username = forms.CharField(max_length=30, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    # add desired fields from Member model (also add to BasicMemberForm)
    member_phone = forms.CharField(
            max_length=coop.models.Member._meta.get_field_by_name(
            'member_phone')[0].max_length, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'member_phone')

class EditMemberForm(AddMemberForm):
    member_id = forms.IntegerField(widget=forms.HiddenInput())
    email_status = forms.CharField(max_length=3, widget=forms.Select(
            choices=(('D', 'Do not email'), ('V', 'Valid'), ('I', 'Invalid'), ('C', 'C?'))))
    is_active = forms.BooleanField(label="Can Login")
    new_pass = forms.CharField(label="New Password", min_length=8, max_length=250, required=False)

    class Meta:
        fields = ('first_name', 'last_name', 'email', 'username',
                'member_phone', 'email_status', 'is_active', 'new_pass')



class MemberEventForm(forms.ModelForm):
    event_type = forms.ModelChoiceField(
            queryset=coop.models.MemberEventType.objects.filter(
                    member_event_type_active=True))
    class Meta:
        model = coop.models.MemberEvent
        fields = ('member', 'event_type', 'member_event_detail')
        widgets = {
            'member': forms.HiddenInput(),
            'member_event_detail': forms.Textarea(attrs={'rows': 5, 'style': 'width: 100%'}),
        }


class AddMemberOptionalForm(forms.Form):
    member_group_id = forms.IntegerField(label="Group ID", required=False)

    def clean_member_group_id(self):
        if self.cleaned_data['member_group_id']:
            try:
                coop.models.MemberGroup.objects.get(pk=self.cleaned_data['member_group_id'])
            except coop.models.MemberGroup.DoesNotExist:
                raise forms.ValidationError("Group %s does not exist." % self.cleaned_data['member_group_id'])

        return self.cleaned_data['member_group_id']


class AddWorkHoursForm(forms.ModelForm):
    class Meta:
        model = coop.models.Work
        fields = ('work_type', 'work_activity', 'work_start_ts', 'work_hours', 'work_note', 'member')
        widgets = { 'work_start_ts': forms.DateTimeInput(),
                'work_note': forms.Textarea(attrs={'rows': 3}),
                'member': forms.HiddenInput(),
                'work_hours': forms.TextInput(attrs={'size': 4, 'onFocus': 'javascript:this.select()'}),
                }


class AddFeeForm(forms.Form):
    import decimal
    data = coop.models.FeeType.objects.filter(fee_type_active=True)
    choices = [ (x.fee_type_id, ('%s ($%.02f)' % (x.fee_type_name,
                            x.fee_amount_default)).replace(' ($0.00)','')) for x in data ]
    fee_type_id = forms.TypedChoiceField(choices = [ ('', '-----') ] + choices,
                coerce=decimal.Decimal, required=True, empty_value='')
    fee_amount = forms.DecimalField(max_digits=8, decimal_places=2)
    fee_note = forms.CharField(max_length=250, required=False)
    paid = forms.BooleanField()






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

import random,time,datetime,re

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout

import coop.forms
import coop.models
import coop.signals
from coop import viewlib

try:
    import coop_custom
    print "Co-op Custom module loaded"
except ImportError:
    coop_custom = None


@login_required()
def default(request):
    print request
    data = viewlib.stats()
    return render(request, 'index.html', {'data': data})

@permission_required('coop.view')
def member_group_view(request, member_group_id):
    """View group info, and all members in group"""
    group = coop.models.MemberGroup.objects.get(pk=member_group_id)
    members = group.group_members.order_by('member__user__last_name',
            'member__user__first_name', 'member__member_id')
    notes = coop.models.MemberEvent.objects.filter(
            member__membergroup=group.member_group_id,
            event_type__in = [1,2])[:10]
    events = coop.models.MemberEvent.objects.filter(
            member__membergroup=group.member_group_id).exclude(
            event_type__in = [1,2])[:10]

    print notes
    print events

    return render(request, 'member_group_view.html', {'group': group,
            'members': members, 'notes': notes, 'events': events})

@permission_required('coop.view')
def member_view(request, member_id=None):
    if not member_id:
        return HttpResponseRedirect('/coop')

    member = coop.models.Member.objects.get(member_id=member_id)
    addresses = member.addresses.filter(address_active=True)
    notes = member.events.filter(event_type__in = [1,2])[:5]
    events = member.events.exclude(event_type__in = [1,2])[:5]

    hours = member.get_work_summary()
    fees = member.get_fee_summary()
    loans = member.get_loan_summary()

    if loans['not_received_count']:
        loans['class'] = 'bg-problem'
        loans['message'] = '%s reqr\'d' % loans['not_received_amount']
        loans['tip'] = 'Oldest unreceived: %s' % loans['oldest_not_received'].strftime('%Y-%d-%m')
    else:
        loans['class'] = 'bg-ok'
        loans['message'] = 'Complete'
        loans['tip'] = 'See details'

    if fees['not_paid_count']:
        fees['class'] = 'bg-problem'
        fees['message'] = '%s owed' % fees['not_paid_amount']
        fees['tip'] = 'Oldest unpaid: %s' % fees['oldest_not_paid'].strftime('%Y-%d-%m')
    else:
        fees['class'] = 'bg-ok'
        fees['message'] = 'Up to date'
        fees['tip'] = 'See details'

    coop.signals.pre_member_view.send(member_view, request=request, data=locals())

    outstanding_fees = coop.models.Fee.objects.select_related(
            'FeeType').filter(member=member, fee_paid_ts__isnull=True)
    fee_form = coop.forms.AddFeeForm()


    return render(request, 'member_view.html',
            {'member': member, 'addresses': addresses, 'notes': notes,
                'events': events, 'hours': hours, 'fees': fees,
                'loans': loans, 'fee_form': fee_form,
                'outstanding_fees': outstanding_fees,
                'add_work_hours_form': coop.forms.AddWorkHoursForm(
                        initial={'member': member.member_id}) })


@permission_required('coop.add_member')
def member_add(request):
    """Display/process add new member form"""
    if request.method == 'POST':
        user = coop.forms.AddMemberForm(request.POST)
        address = coop.forms.BasicAddressForm(request.POST)
        optional = coop.forms.AddMemberOptionalForm(request.POST)
        user_is_valid = user.is_valid()
        address_is_valid = address.is_valid()
        optional_is_valid = optional.is_valid()
        if user_is_valid and address_is_valid and optional_is_valid:
            if not user.cleaned_data['username']:
                user.cleaned_data['username'] = 'temp%06d' % random.randint(0,999999)
            new_user = User.objects.create(username=user.cleaned_data['username'],
                    first_name=user.cleaned_data['first_name'],
                    last_name=user.cleaned_data['last_name'],
                    email=user.cleaned_data['email'],
                    is_active=False, # no one is allowed to login by default
                    is_staff=False,
                    is_superuser=False,
                    last_login=datetime.datetime(1900,1,1))
            new_user.save()
            new_member = coop.models.Member.objects.create(user=new_user,
                    member_status_id=1,
                    email_status='V',
                    member_phone=user.cleaned_data['member_phone'])
            new_member.save()

            if address.has_data():
                new_address = coop.models.Address.objects.create(member=new_member,
                        address_line1 = address.cleaned_data['address_line1'],
                        address_line2 = address.cleaned_data['address_line2'],
                        postal_code = address.cleaned_data['postal_code'],
                        city = address.cleaned_data['city'],
                        address_active = True,
                )
                new_address.save()
            else:
                new_address = None

            # attach member to group if specified
            if optional.cleaned_data['member_group_id']:
                member_group = coop.models.MemberGroupMember.objects.create(
                        member_group_id=optional.cleaned_data['member_group_id'],
                        member_id=new_member.member_id,
                        member_group_rep=False)
                member_group.save()
            else:
                member_group = None

            # XXX check for "required" loans and add them

            coop.signals.post_member_add_save.send(member_add,
                        request=request, user=new_user,
                        member=new_member, address=new_address,
                        member_group=member_group)


            return HttpResponseRedirect('/coop/member/%s' % new_member.member_id)
    else:
        user = coop.forms.AddMemberForm()
        address = coop.forms.BasicAddressForm()
        optional = coop.forms.AddMemberOptionalForm(request.GET)

    coop.signals.pre_member_add_form.send(member_add, user=user,
            address=address, optional=optional)

    return render(request, 'member_add_form.html',
            {'user_form': user, 'address': address, 'optional': optional})

@permission_required('coop.view')
def member_search(request):
    q = (request.GET.get('q') or '').strip()
    pg = int(request.GET.get('pg') or 0) or 1
    search_type = 'Unknown'
    data = []

    sort = {
        'relevance': ('member__member_status', '-rank',
                    'member__user__last_name', 'member__user__first_name',
                    'member'),
        'last_name': ('member__member_status', 'member__user__last_name', 'member__user__first_name', 'member'),
        'join_date': (),
    }

    if q:
        if q[-1] == '*' and (' ' not in q):
            search_type = "last name"
            # last name search
            data = coop.models.MemberFts.objects.filter(
                    member__user__last_name__istartswith=q.strip('*')
                    ).order_by(*sort['last_name'])
        else:
            search_type = "keyword"
            # keyword search
            data = coop.models.MemberFts.objects.extra(
                    select={'rank': "ts_rank_cd(member_fts, plainto_tsquery(%s), 4)",
                            'headline': 'ts_headline(member_text, plainto_tsquery(%s), \'MaxFragments=1 MinWords=3 MaxWords=20\')'},
                    select_params=[q,q],
                    where =["member_fts @@ plainto_tsquery(%s)"],
                    params=[q],
                    ).select_related().order_by(*sort['relevance'])

                    #).filter(member_id__member_status = 'A'

    if data and (not request.GET.get('status') == 'all'):
        data = data.filter(member__member_status = 1)

    if len(data) == 1:
        return HttpResponseRedirect('/coop/member/%d' % data[0].member_id)

    page = Paginator(data, 25).page(pg)

    return render(request, 'member_search.html',
            {'results': page, 'q': q or '', 'QUERY_STRING': re.sub(
            r'&?pg=\d+', '', request.META['QUERY_STRING']),
            'status':request.GET.get('status')})

@permission_required('coop.change_member')
def member_update(request):
    """All member updates are routed through this function"""

    if request.POST.get('add-note'):
        viewlib.logEvent(request, 1, request.POST['member_id'],
                request.POST['member_event_detail'])

    if request.POST.get('resign'):
        if request.POST.get('confirm-resign'):
            member = coop.models.Member.objects.get(pk=request.POST['member_id'])
            member.member_resigned_date = datetime.datetime.today()
            member.member_status_id = 3
            member.save()
            member.user.is_active = False
            member.user.save()
            viewlib.logEvent(request, 3, request.POST['member_id'],
                    request.POST.get('resign-reason') or '')

    if request.POST.get('reactivate'):
        if request.POST.get('confirm-reactivate'):
            member = coop.models.Member.objects.get(pk=request.POST['member_id'])
            member.member_status_id = 1
            member.save()
            viewlib.logEvent(request, 4, request.POST['member_id'], 're-activating')

    if request.POST.get('add-hours'):
        hours = coop.forms.AddWorkHoursForm(request.POST)
        if hours.is_valid():
            hours.save()
            msg = '%s: %s hours' % (
                    hours.cleaned_data['work_type'].work_name,
                    hours.cleaned_data['work_hours'])
            if hours.cleaned_data['work_note']:
                msg += '. ' + hours.cleaned_data['work_note']
            viewlib.logEvent(request, 5,
                    hours.cleaned_data['member'].member_id, msg)
        else:
            print "Silent fail: invalid hours data: %s" % (hours.errors,)

    if request.POST.get('add-fee'):
        member_id = request.POST['member_id']

        paid = []
        for k in request.POST.keys():
            if k.startswith('pay-'):
                fee = coop.models.Fee.objects.get(pk=k[4:])
                fee.fee_paid_ts = datetime.datetime.now()
                fee.save()
                paid.append(fee)

        viewlib.logEvent(request, 8, member_id, "Paid fee (%s)" % (', '.join(
                ['%s #%s' % (x.fee_type.fee_type_name, x.fee_id) for x in paid])))

        if request.POST.get('fee_type_id') and request.POST.get('fee_amount'):
            try:
                message = ''
                data = { 'fee_type_id': request.POST['fee_type_id'],
                         'fee_amount': re.sub('[^\d.]', '', request.POST['fee_amount']),
                         'fee_note': request.POST['fee_note'] or '',
                         'member_id': member_id,
                         'fee_ts': datetime.datetime.now(),
                        }
                if request.POST.get('paid'):
                    data['fee_paid_ts'] = datetime.datetime.now()
                    mesage = ' (paid)'

                fee = coop.models.Fee.objects.create(**data)
                fee.save()

                if fee.fee_note:
                    message = '%s: %s' % (message, fee.fee_note)
                message = 'Add %s%s' % (fee.fee_type.fee_type_name, message)

                viewlib.logEvent(request, 8, member_id, message)
            except:
                raise

    return HttpResponseRedirect('/coop/member/%d' % int(
            request.POST.get('member_id') or request.POST.get('member')))

def random_member(request):
    """Redirect to a random active member"""
    members = coop.models.Member.objects.filter(member_status=1).values('member_id')
    if members:
        return HttpResponseRedirect('/coop/member/%d' % random.choice(members)['member_id'])
    return HttpResponseRedirect('/coop?error=No members found')

def random_group(request):
    """Redirect to a random group with more than one member (if possible)"""
    groups = coop.models.MemberGroupMember.objects.values('member_group'
            ).annotate(count=Count('member_group')).filter(count__gt=1)
    if groups:
        return HttpResponseRedirect('/coop/member/group/%d' % random.choice(groups)['member_group'])
    return HttpResponseRedirect('/coop?error=No groups found')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/coop/')

def member_edit(request, member_id=None):
    instance = coop.models.Member.objects.get(pk=member_id)
    queryset=coop.models.Address.objects.filter(member=instance)
    if request.method == 'POST':
        member_form = coop.forms.EditMemberForm(request.POST, instance=instance.user)
        addresses = coop.forms.AddressFormSet(request.POST,
                queryset=queryset, prefix="address")
        if member_form.is_valid() and addresses.is_valid():
            member = coop.forms.BasicMemberForm(request.POST, instance=instance)
            changes = []
            if member_form.has_changed():
                changes.extend(member_form._changed_data)
                # XXX these fields always appear in changes due to being added to form
                # based on User model, but obviously not in the User instance.
                if 'new_pass' in changes:
                    changes.remove('new_pass')
                changes.remove('member_id')
                changes.remove('email_status')
                # changes to User need to update Member timestamp
                instance.member_update_ts = datetime.datetime.now()
                instance.save()
            if member.has_changed():
                changes.extend(member._changed_data)

            for a in addresses:
                if a.has_changed():
                    changes.extend(a._changed_data)

            member_form.save()
            addresses.save()
            member.save()

            newpass = request.POST.get('new_pass')
            if newpass and (not instance.user.check_password(newpass)):
                instance.user.set_password(newpass)
                instance.user.save()
                changes.append('password')

            if changes:
                viewlib.logEvent(request, 7, member_id, "Updated "+', '.join(changes))

            return HttpResponseRedirect('/coop/member/%s' % member_id)

    else:
        member_form = coop.forms.EditMemberForm(
                instance=instance.user,
                initial={'member_phone': instance.member_phone,
                        'member_id': instance.member_id})
        addresses = coop.forms.AddressFormSet(prefix="address",
                queryset=queryset)

    return render(request, 'member_edit_form.html',
            {'member_id': member_id, 'user_form': member_form, 'address': addresses, 'member': instance})


def test(request, member_id=None):
    member_id='11689'
    member = coop.models.Member.objects.get(pk=member_id)

    return render(request, 'test.html', {'fee_form': form, 'fees': fees, 'member': member})



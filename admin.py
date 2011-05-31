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

from django.db.models import get_models, get_app
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from km.coop.models import *


class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'value']
admin.site.register(AppSettings, AppSettingsAdmin)

class MemberGroupTypeAdmin(admin.ModelAdmin):
    list_display = ['member_group_type_id', 'member_group_type_label',
            'member_group_type_active', 'member_group_type_ts']
admin.site.register(MemberGroupType, MemberGroupTypeAdmin)

class MemberFlagTypeAdmin(admin.ModelAdmin):
    list_display = ['member_flag_type_id', 'member_flag_type_label',
            'member_flag_type_active', 'member_flag_type_ts']
admin.site.register(MemberFlagType, MemberFlagTypeAdmin)

class RoleTypeAdmin(admin.ModelAdmin):
    list_display = ['role_type_id', 'role_type_label',
            'role_type_active', 'role_type_ts']
admin.site.register(RoleType, RoleTypeAdmin)

class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['loan_type_id', 'loan_name', 'loan_amount_default',
            'loan_type_active', 'loan_required', 'loan_type_ts', ]
admin.site.register(LoanType, LoanTypeAdmin)

class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ['work_type_id', 'work_name', 'work_amount_default',
            'work_type_active', 'work_type_ts', ]
admin.site.register(WorkType, WorkTypeAdmin)

class WorkActivityAdmin(admin.ModelAdmin):
    list_display = ['work_activity_id', 'activity_name',
            'work_activity_active', 'work_activity_ts', ]
admin.site.register(WorkActivity, WorkActivityAdmin)

class RewardTypeAdmin(admin.ModelAdmin):
    list_display = ['reward_type_id', 'reward_name', 'reward_amount',
            'reward_type_active', 'reward_type_ts', ]
admin.site.register(RewardType, RewardTypeAdmin)


class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ['fee_type_id', 'fee_type_name', 'fee_amount_default',
            'fee_recurring', 'fee_type_active', 'fee_type_ts', ]
admin.site.register(FeeType, FeeTypeAdmin)





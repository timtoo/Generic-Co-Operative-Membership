-- extra SQL for Karma database

-- CHECK: SELECT * FROM member_flag_type where member_flag_type_label like 'Old Database%'

INSERT INTO member_flag_type (member_flag_type_id, member_flag_type_label, member_flag_type_description, member_flag_type_active, member_flag_type_has_detail, member_flag_type_ts, member_flag_type_system, member_flag_detail_options) VALUES (101,'Old Database Hid', 'The "House ID" in the old MS Access database', true, true, current_timestamp, false, '');
INSERT INTO member_flag_type (member_flag_type_id, member_flag_type_label, member_flag_type_description, member_flag_type_active, member_flag_type_has_detail, member_flag_type_ts, member_flag_type_system, member_flag_detail_options) VALUES (102, 'Old Database PrevHid', 'The "Previous House ID" in the old MS Access database', true, true, current_timestamp, false, '');

INSERT INTO member_group_type (member_group_type_id, member_group_type_label, member_group_type_description, member_group_type_active, member_group_type_auto_create, member_group_type_unique, member_group_type_share_hours, member_group_type_ts) VALUES (1, 'Household', 'A group of members that can share work hours', true, true, true, true, current_timestamp);



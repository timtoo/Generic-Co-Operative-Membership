Looking up Members
==================

One of the central activities of the membership database is
looking up members. To make this as simple and as fast as possible
the membership lookup works a lot like Google. Just type whatever
information wanted to be searched for, and all of the text assocated
with a member will be searched.

CREATE OR REPLACE FUNCTION member_text(integer) RETURNS text AS $$
DECLARE
    rec record;
    out text := '';
BEGIN

    select
        first_name,
        last_name,
        username,

        email,
        member_phone,
        CASE WHEN member_status = 'A' THEN 'active'
             WHEN member_status = 'R' THEN 'resigned'
             WHEN member_status = 'D' THEN 'deleted'
        ELSE 'unknown'
        END AS status
    INTO rec
    FROM member JOIN auth_user ON (django_user_id=auth_user.id)
    WHERE member.member_id=$1;

    out := out || trim(' ' from coalesce(rec.first_name, '') || ' ' || coalesce(rec.last_name, ''));
    out := out || ' (' || rec.username || ')';

    out := out || E'\n--\n';

    out := out || trim(E'\n' from rec.email || E'\n' || rec.member_phone);

    out := out || E'\n\n';

    FOR rec IN select * FROM address JOIN city USING (city_id) WHERE member_id=$1
    LOOP
        out := out || trim(E'\n' from rec.address_line1 || E'\n' || rec.address_line2) || E'\n';
        out := out || trim(E' ' from rec.postal_code || ' ' || rec.city_name) || E'\n';
        out := out || E'\n';

    END LOOP;

    out := trim(E'\n' from out) || E'\n--\n';

    select
        CASE WHEN member_status = 'A' THEN 'active'
             WHEN member_status = 'R' THEN 'resigned'
             WHEN member_status = 'D' THEN 'deleted'
        ELSE 'unknown'
        END AS status
    INTO rec
    FROM member
    WHERE member.member_id=$1;

    out := out || rec.status;

    RETURN out;
END
$$ LANGUAGE plpgsql;



select member.member_id,

setweight(to_tsvector(
    coalesce(first_name, '') || ' ' ||
    coalesce(last_name, '') || ' ' ||
    coalesce(username, '')
    ), 'A') ||
setweight(to_tsvector(
    coalesce(email, '') || ' ' ||
    member_phone || ' ' ||
    coalesce(city_name, '') || ' ' ||
    coalesce(address_line1, '') || ' ' ||
    coalesce(address_line2, '') || ' ' ||
    coalesce(postal_code, '') || ' ' ||
    coalesce(cast(member_group_id AS text), '')
    ), 'B') ||
setweight(to_tsvector(
    CASE WHEN member_status = 'A' THEN 'active'
         WHEN member_status = 'R' THEN 'resigned'
         WHEN member_status = 'D' THEN 'deleted'
    ELSE 'unknown'
    END
    ), 'C')
AS member_fts

from member
LEFT OUTER JOIN auth_user ON (django_user_id=auth_user.id)
LEFT OUTER JOIN address ON (member.member_id = address.member_id AND address_active=true)
LEFT OUTER JOIN city USING (city_id)
LEFT OUTER JOIN (SELECT member_id, member_group.member_group_id FROM member_group_member
        JOIN member_group ON (member_group_member.member_group_id=member_group.member_group_id
                AND member_group_type_id=1)) AS mg ON (member.member_id=mg.member_id)

;


tables: auth_user, member, address, member_group

create table member_fts (
    member_id integer references member(member_id) primary key not null,
    member_fts  tsvector
);




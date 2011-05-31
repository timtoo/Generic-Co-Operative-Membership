-- This file is imported on a post_syncdb signal.
-- It is executed in chunks, split using any SQL comments.
-- (so put an sql comment before each block of code to execute,
-- but not in the middle of any SQL statements)
-- Before each block a comment can specify an SQL statement to use
-- to test if the block should be run. If the SQL statement returns
-- any records then the block is not run.
-- Example: -- CHECK: SELECT * from my_table WHERE some_field = expected_val;

-- CHECK: SELECT * FROM pg_language WHERE lanname='plpgsql'
CREATE LANGUAGE plpgsql;

-- see: http://www.laudatio.com/wordpress/2008/11/05/postgresql-83-to_ascii-utf8/
CREATE OR REPLACE FUNCTION to_ascii(bytea, name)
RETURNS text STRICT AS 'to_ascii_encname' LANGUAGE internal;

-- convert all non-word character sequences to underscore for matching purposes.
-- this will work at least for latin-1 covered languages.
CREATE OR REPLACE FUNCTION ascii_normalize(text)
RETURNS text IMMUTABLE LANGUAGE SQL AS $$
SELECT lower(regexp_replace(to_ascii(convert_to($1, 'latin1'), 'latin1'), '[^A-Za-z0-9]+', '_', 'g'))
$$;

-- INCLUDE: setupdb_country.sql

-- province normalize

CREATE OR REPLACE FUNCTION province_normalize() RETURNS TRIGGER AS $$
BEGIN
    NEW.province_norm := ascii_normalize(NEW.province_name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- CHECK: SELECT * FROM pg_trigger WHERE tgname = 'province_normalize_t'

CREATE TRIGGER province_normalize_t
BEFORE INSERT OR UPDATE ON province
    FOR EACH ROW EXECUTE PROCEDURE province_normalize();

-- city normalize

CREATE OR REPLACE FUNCTION city_normalize() RETURNS TRIGGER AS $$
BEGIN
   NEW.city_norm := ascii_normalize(NEW.city_name);
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- CHECK: SELECT * FROM pg_trigger WHERE tgname = 'city_normalize_t'

CREATE TRIGGER city_normalize_t
BEFORE INSERT OR UPDATE ON city
    FOR EACH ROW EXECUTE PROCEDURE city_normalize();

-- insert provinces
-- CHECK: SELECT * FROM province WHERE country_id = 124

INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (5883102, 48, 'Alberta', 'alberta', 'AB', 124, 'CA.01');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (5909050, 59, 'British Columbia', 'british_columbia', 'BC', 124, 'CA.02');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6065171, 46, 'Manitoba', 'manitoba', 'MB', 124, 'CA.03');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6087430, 13, 'New Brunswick', 'new_brunswick', 'NB', 124, 'CA.04');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6354959, 10, 'Newfoundland and Labrador', 'newfoundland', 'NL', 124, 'CA.05');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6091530, 12, 'Nova Scotia', 'nova_scotia', 'NS', 124, 'CA.07');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6093943, 35, 'Ontario', 'ontario', 'ON', 124, 'CA.08');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6113358, 11, 'Prince Edward Island', 'prince_edward_island', 'PE', 124, 'CA.09');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6115047, 24, 'Quebec', 'quebec', 'QC', 124, 'CA.10');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6141242, 47, 'Saskatchewan', 'saskatchewan', 'SK', 124, 'CA.11');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6091069, 61, 'Northwest Territories', 'northwest_territories', 'NT', 124, 'CA.13');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6091732, 62, 'Nunavut', 'nunavut', 'NT', 124, 'CA.14');
INSERT INTO province (province_id, prcode, province_name, province_norm, province_code, country_id, admin1) VALUES (6185811, 60, 'Yukon', 'yukon', 'YT', 124, 'CA.12');


CREATE TABLE coop_memberfts (
    member_id integer references coop_member(member_id) primary key not null,
    member_text text not null,
    member_fts tsvector not null,
    member_fts_ts timestamp default current_timestamp
);


-- Create a text representation of all the info we want to make full-text searchable
CREATE OR REPLACE FUNCTION coop_member_text(integer) RETURNS text AS $$
DECLARE
    rec record;
    out text := '';
BEGIN
    select
            first_name,
            last_name,
            username,
            email,
            member_phone
        INTO rec
        FROM coop_member JOIN auth_user ON (django_user_id=auth_user.id)
        WHERE coop_member.member_id=$1;

    out := out || trim(' ' from coalesce(rec.first_name, '') || ' ' || coalesce(rec.last_name, ''));
    out := out || ' (' || rec.username || ')';

    out := out || E'\n--\n';

    out := out || trim(E'\n' from rec.email || E'\n' || rec.member_phone);

    out := out || E'\n\n';

    FOR rec IN select * FROM coop_address JOIN city USING (city_id) WHERE member_id=$1
    LOOP
        out := out || trim(E'\n' from rec.address_line1 || E'\n' || rec.address_line2) || E'\n';
        out := out || trim(E' ' from rec.city_name || '  ' || rec.postal_code) || E'\n';
        out := out || E'\n';

    END LOOP;

    out := trim(E'\n' from out) || E'\n--\n';

    select member_id,
            CASE WHEN member_status_id = 1 THEN 'active'
                 WHEN member_status_id = 2 THEN 'inactive'
                 WHEN member_status_id = 3 THEN 'resigned'
                 WHEN member_status_id = 4 THEN 'deleted'
                 WHEN member_status_id = 0 THEN 'unknown'
            ELSE '???'
            END AS status
        INTO rec
        FROM coop_member
        WHERE coop_member.member_id=$1;

    out := out || rec.status;
    out := out || E'\nM#' || cast($1 AS text);

    SELECT member_group_id INTO rec FROM coop_membergroupmember
        JOIN coop_membergroup USING (member_group_id)
        WHERE member_id=$1 and member_group_type_id=1
        ORDER BY member_group_member_ts DESC
        LIMIT 1;

    If rec IS NOT NULL THEN
        out := out || ' H#' || cast(rec.member_group_id AS text);
    END IF;

    RETURN out;
END
$$ LANGUAGE plpgsql;

-- take the index text and create weighted tsvector from the sections.
CREATE OR REPLACE FUNCTION coop_member_tsvector(integer) RETURNS tsvector AS $$
DECLARE
    tmp text;
BEGIN
    SELECT coop_member_text($1) INTO tmp;
    RETURN coop_member_tsvector(tmp);
END
$$ LANGUAGE plpgsql;

-- take the index text and create weighted tsvector from the sections.
CREATE OR REPLACE FUNCTION coop_member_tsvector(text) RETURNS tsvector AS $$
BEGIN
    RETURN setweight(to_tsvector(split_part($1, E'\n\n', 1)), 'A') ||
           setweight(to_tsvector(split_part($1, E'\n\n', 2)), 'B') ||
           setweight(to_tsvector(split_part($1, E'\n\n', 3)), 'C');
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION coop_member_update_fts(integer) RETURNS tsvector AS $$
DECLARE
    mtxt text;
    mfts tsvector;
BEGIN
    SELECT coop_member_text($1) INTO mtxt;
    SELECT coop_member_tsvector(mtxt) INTO mfts;
    delete from coop_memberfts where member_id=$1;
    insert into coop_memberfts (member_id, member_text, member_fts, member_fts_ts)
            VALUES ($1, mtxt, mfts, current_timestamp);
    return mfts;
END
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION coop_member_id_trigger() RETURNS trigger AS $$
begin
    perform coop_member_update_fts(new.member_id);
    return new;
end
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION auth_user_member_id_trigger() RETURNS trigger AS $$
DECLARE
    mid integer;
BEGIN
    SELECT member_id INTO mid FROM coop_member where django_user_id=new.id;
    IF mid IS NOT NULL THEN
        perform coop_member_update_fts(mid);
    END IF;
    RETURN new;
END
$$ LANGUAGE plpgsql;

-- CHECK: SELECT * FROM pg_trigger WHERE tgname='coop_member_aiu_t'
CREATE TRIGGER coop_member_aiu_t AFTER INSERT OR UPDATE
ON coop_member FOR EACH ROW EXECUTE PROCEDURE coop_member_id_trigger();

-- CHECK: SELECT * FROM pg_trigger WHERE tgname='coop_address_aiu_t'
CREATE TRIGGER coop_address_aiu_t AFTER INSERT OR UPDATE
ON coop_address FOR EACH ROW EXECUTE PROCEDURE coop_member_id_trigger();

-- CHECK: SELECT * FROM pg_trigger WHERE tgname='auth_user_aiu_t'
CREATE TRIGGER auth_user_aiu_t AFTER INSERT OR UPDATE
ON auth_user FOR EACH ROW EXECUTE PROCEDURE auth_user_member_id_trigger();

-- CHECK: SELECT * FROM coop_memberstatus
INSERT INTO coop_memberstatus VALUES (0, 'Unknown');
INSERT INTO coop_memberstatus VALUES (1, 'Active');
INSERT INTO coop_memberstatus VALUES (2, 'Inactive');
INSERT INTO coop_memberstatus VALUES (3, 'Resigned');
INSERT INTO coop_memberstatus VALUES (4, 'Deleted');


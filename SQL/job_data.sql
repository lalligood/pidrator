drop table if exists job_data;

create table job_data (
    id serial primary key
    , job_id uuid
    , moment timestamp with time zone
    , temperature double precision
    )

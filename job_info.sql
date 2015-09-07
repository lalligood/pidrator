drop table if exists job_info;

create table job_info (
    id uuid not null default uuid_generate_v4()
    , jobname text not null unique
    , user_id uuid
    , device_id uuid
    , food_id uuid
    , temperature_deg int
    , temperature_setting text
    , createtime timestamp with time zone default now()
    , starttime timestamp with time zone
    , endtime timestamp with time zone
    , constraint job_info_pkey primary key (id)
    )

drop table if exists devices;

create table devices (
    id uuid not null default uuid_generate_v4()
    , devicename text not null unique
    , createdate timestamp with time zone default now()
    , constraint devices_pkey primary key (id)
    )

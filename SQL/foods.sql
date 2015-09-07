drop table if exists foods;

create table foods (
    id uuid not null default uuid_generate_v4()
    , foodname text not null unique
    , createdate timestamp with time zone default now()
    , constraint foods_pkey primary key (id)
    )

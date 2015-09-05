drop table if exists users;

create table users (
    id uuid not null default uuid_generate_v4()
    , username text not null
    , fullname text not null
    , email_address text not null
    , "password" text not null
    , createdate timestamp with time zone default now()
    , constraint users_pkey primary key (id)
    )

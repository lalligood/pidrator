drop table if exists foodcomments;

create table foodcomments (
    jobinfo_id uuid not null
    , foodcomments text
    , createtime timestamp with time zone default now()
    );
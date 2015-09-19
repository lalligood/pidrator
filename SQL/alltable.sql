-- Make sure that uuid-ossp & pgcrypto extensions are installed
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- Drop any existing tables if they exist
drop table if exists devices;
drop table if exists foodcomments;
drop table if exists foods;
drop table if exists job_data;
drop table if exists job_info;
drop table if exists users;

-- Create all tables
create table devices (
    id uuid not null default uuid_generate_v4()
    , devicename text not null unique
    , createdate timestamp with time zone default now()
    , constraint devices_pkey primary key (id)
    );

create table foodcomments (
    jobinfo_id uuid not null
    , foodcomments text
    , createtime timestamp with time zone default now()
    );

create table foods (
    id uuid not null default uuid_generate_v4()
    , foodname text not null unique
    , createdate timestamp with time zone default now()
    , constraint foods_pkey primary key (id)
    );

create table job_data (
    id serial
    , job_id uuid
    , moment timestamp with time zone
    , temperature double precision
    , constraint job_data_pkey primary key (id)
    );

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
    , cookminutes int
    , constraint job_info_pkey primary key (id)
    );

create table users (
    id uuid not null default uuid_generate_v4()
    , username text not null unique
    , fullname text not null
    , email_address text not null unique
    , "password" text not null
    , createdate timestamp with time zone default now()
    , constraint users_pkey primary key (id)
    );

-- If desired, you can pre-populate some tables with sample data
-- by removing /* & */
/*
insert into devices (devicename) values
    ('slow cooker')
    , ('dehydrator')
    returning *;

insert into foods (foodname) values
    ('beef jerky')
    , ('pineapple')
    , ('BBQ pulled pork')
    , ('BBQ beef brisket')
    returning *;

-- Replace bogus values with your own information below
insert into users (username, fullname, email_address, password) values
    ('<your_username>', '<your_name>', '<your_email_address>', crypt('<your_password>', gen_salt('bf')))
    returning *;
*/

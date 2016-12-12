/*

pidrator_SQL.sql

Contains all SQL for initial creation & configuration of pidrator database

*/

-- ================
-- INITIAL CREATION
-- ================

-- Create database user
create user pi createdb login connection limit 2 encrypted password 'pidrator';

-- Create database
create database pidrator owner pi;

-- Create necessary extensions: uuid-ossp & pgcrypto
create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;

-- Create tables
--drop table comments;
create table if not exists comments (
    id uuid not null default uuid_generate_v4()
    , cookjob_id uuid not null
    , user_id uuid not null
    , usercomment text
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint comments_pkey primary key (id)
    );

--drop table cookjobs;
create table if not exists cookjobs (
    id uuid not null default uuid_generate_v4()
    , user_id uuid not null
    , device_id uuid not null
    , food_id uuid not null
    , jobname text not null unique
    , temperature text
    , startedat timestamp with time zone
    , endedat timestamp with time zone
    , cookminutes int
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint cookjobs_pkey primary key (id)
    );

--drop table devices;
create table if not exists devices (
    id uuid not null default uuid_generate_v4()
    , user_id uuid not null
    , devicename text not null unique
    , devicedescription text
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint devices_pkey primary key (id)
    );

--drop table favorites;
create table if not exists favorites (
    id uuid not null default uuid_generate_v4()
    , user_id uuid not null
    , cookjob_id uuid not null
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint favorites_pkey primary key (id)
    );

--drop table foods;
create table if not exists foods (
    id uuid not null default uuid_generate_v4()
    , user_id uuid not null
    , foodname text not null unique
    , fooddescription text
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint foods_pkey primary key (id)
    );

--drop table tracking;
create table if not exists tracking (
    id serial
    , job_id uuid not null
    , capturedat timestamp with time zone default now()
    , temp_c double precision
    , temp_f double precision
    , constraint tracking_pkey primary key (id)
    );

--drop table users;
create table if not exists users (
    id uuid not null default uuid_generate_v4()
    , username text not null unique
    , userpswd text not null
    , fullname text not null unique
    , email text not null unique
    , createdat timestamp with time zone default now()
    , updatedat timestamp with time zone default now()
    , constraint users_pkey primary key (id)
    );

-- ===================
-- APPLICATION ACTIONS
-- ===================

-- Insert new user
prepare add_user as
    insert into users (username, userpswd, fullname, email)
        values ($1, crypt($2, gen_salt('bf'), $3, $4)
;

--execute add_user ();
--deallocate add_user;

-- Update existing user
prepare edit_user as
    update users
        set userpswd = $1
            , fullname = $2
            , email = $3
            , updatedat = now()
    where username = $4
;

--execute edit_user ();
--deallocate edit_user;

-- Remove user
prepare delete_user as
    delete from users
    where username = $1
        and userpswd = crypt($2, userpswd)
;

--execute delete_user ();
--deallocate delete_user;

-- Login user
prepare login_user as
    select true
    from users
    where username = $1
        and userpswd = crypt($2, userpswd)
;

--execute login_user ();
--deallocate login_user;

-- Insert new device
prepare add_device as
    insert into devices (devicename, devicedescription, user_id)
        values ($1, $2, $3)
;

--execute add_device ();
--deallocate add_device;

-- Update existing device
prepare edit_device as
    update devices
        set devicename = $1
            , devicedescription = $2
            , user_id = $3
            , updatedat = now()
    where devicename = $4
;

--execute edit_device ();
--deallocate edit_device;

-- Remove existing device
prepare delete_device as
    delete from devices
    where devicename = $1
        and user_id = $2
;

--execute delete_device ();
--deallocate delete_device;

prepare list_device as
    select *
    from devices
    where user_id = $1
;

--execute list_device ();
--deallocate list_device;

-- Insert new food
prepare add_food as
    insert into foods (foodname, fooddescription, user_id)
        values ($1, $2, $3)
;

--execute add_food ();
--deallocate add_food;

-- Update existing food
prepare edit_food as
    update foods
        set foodname = $1
            , fooddescription = $2
            , user_id = $3
            , updatedat = now()
    where foodname = $4
;

--execute edit_food ();
--deallocate edit_food;

-- Remove existing food
prepare delete_food as
    delete from foods
    where foodname = $1
        and user_id = $2
;

--execute delete_food ();
--deallocate delete_food;

prepare list_food as
    select *
    from foods
    where user_id = $1
;

--execute list_food ();
--deallocate list_food;


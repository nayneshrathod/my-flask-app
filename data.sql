create database flog_db;
use flog_db;

drop table user;
drop table blog;

truncate user;
truncate blog;

create table user(
user_id  int auto_increment primary key,
first_name varchar(30) not null,
last_name varchar(30) not null,
email varchar(50) unique not null, 
username varchar(40) unique  not null,
password varchar(150) not null
);

create table blog(
blog_id  int auto_increment primary key,
title varchar(100) not null,
author varchar(40) not null,
body varchar(10000)   not null 
);

desc user;
desc blog;

select * from user;
select * from blog;

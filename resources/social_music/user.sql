create table if not exists user
(
    id         int auto_increment
        constraint `PRIMARY`
        primary key,
    email      varchar(255) null,
    first_name varchar(255) not null,
    gender     varchar(25)  null,
    last_name  varchar(255) null,
    ref_aa     int          not null,
    constraint user_ref_aa_uindex
        unique (ref_aa)
);


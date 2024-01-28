create table if not exists descriptors
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint descriptors_descripption_uindex
        unique (description)
);


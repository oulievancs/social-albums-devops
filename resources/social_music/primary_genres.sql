create table if not exists primary_genres
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint primary_genres_description_uindex
        unique (description)
);


create table if not exists secondary_genres
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint secondary_genres_description_uindex
        unique (description)
);


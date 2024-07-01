create database if not exists social-music;

use social-music;

create table if not exists primary_genres
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint primary_genres_description_uindex
        unique (description)
);

create table if not exists secondary_genres
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint secondary_genres_description_uindex
        unique (description)
);

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

create table if not exists artist
(
    id     int auto_increment
        constraint `PRIMARY`
        primary key,
    year   int          null,
    name   varchar(255) not null,
    ref_aa int          not null,
    constraint artist_ref_aa_uindex
        unique (ref_aa)
);

create table if not exists album
(
    id           int auto_increment
        constraint `PRIMARY`
        primary key,
    name         varchar(255) not null,
    reviews      int          null,
    avg_rating   double       null,
    ratings      int          null,
    artist_id    int          not null,
    release_date date         null,
    constraint album_artist_id_fk
        foreign key (artist_id) references artist (id)
);

create index album_artist_id_index
    on album (artist_id);

create index album_name_index
    on album (name);

create table if not exists descriptors
(
    id          int auto_increment
        constraint `PRIMARY`
        primary key,
    description varchar(255) not null,
    constraint descriptors_descripption_uindex
        unique (description)
);

create table if not exists descriptors_asoc
(
    id              int auto_increment
        constraint `PRIMARY`
        primary key,
    artist_id       int         not null,
    descriptor_id   int         not null,
    descriptor_type varchar(30) not null,
    constraint descriptors_asoc_artist_id_fk
        foreign key (artist_id) references artist (id)
);

create index descriptors_asoc_artist_id_descriptor_id_index
    on descriptors_asoc (artist_id, descriptor_id);

create index descriptors_asoc_descriptor_type_index
    on descriptors_asoc (descriptor_type);

create table if not exists friendship
(
    id             int auto_increment
        constraint `PRIMARY`
        primary key,
    user_id        int not null,
    friend_user_id int not null,
    constraint friendship_user_id_fk
        foreign key (user_id) references user (id),
    constraint friendship_user_id_fk_2
        foreign key (friend_user_id) references user (id)
);

create index friendship_user_id_index
    on friendship (user_id);

create table if not exists listen
(
    id        int auto_increment
        constraint `PRIMARY`
        primary key,
    user_id   int not null,
    artist_id int not null,
    constraint listen_artist_id_fk
        foreign key (artist_id) references artist (id),
    constraint listen_user_id_fk
        foreign key (user_id) references user (id)
);


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


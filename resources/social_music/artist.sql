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


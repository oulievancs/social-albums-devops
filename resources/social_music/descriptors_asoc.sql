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


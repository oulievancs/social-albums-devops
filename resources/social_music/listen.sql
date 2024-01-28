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


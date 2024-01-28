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


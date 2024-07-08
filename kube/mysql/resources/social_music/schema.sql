CREATE DATABASE IF NOT EXISTS social_music;

USE social_music;

CREATE TABLE IF NOT EXISTS primary_genres (
    id INT AUTO_INCREMENT,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT primary_genres_description_uindex UNIQUE (description),
    CONSTRAINT primary_genres_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS secondary_genres (
    id INT AUTO_INCREMENT,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT secondary_genres_description_uindex UNIQUE (description),
    CONSTRAINT secondary_genres_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT,
    email VARCHAR(255) NULL,
    first_name VARCHAR(255) NOT NULL,
    gender VARCHAR(25) NULL,
    last_name VARCHAR(255) NULL,
    ref_aa INT NOT NULL,
    CONSTRAINT users_ref_aa_uindex UNIQUE (ref_aa),
    CONSTRAINT users_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS artist (
    id INT AUTO_INCREMENT,
    year INT NULL,
    name VARCHAR(255) NOT NULL,
    ref_aa INT NOT NULL,
    CONSTRAINT artist_ref_aa_uindex UNIQUE (ref_aa),
    CONSTRAINT artist_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS album (
    id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    reviews INT NULL,
    avg_rating DOUBLE NULL,
    ratings INT NULL,
    artist_id INT NOT NULL,
    release_date DATE NULL,
    CONSTRAINT album_artist_id_fk FOREIGN KEY (artist_id) REFERENCES artist (id),
    CONSTRAINT album_pk PRIMARY KEY (id)
);

CREATE INDEX album_artist_id_index ON album (artist_id);
CREATE INDEX album_name_index ON album (name);

CREATE TABLE IF NOT EXISTS descriptors (
    id INT AUTO_INCREMENT,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT descriptors_description_uindex UNIQUE (description),
    CONSTRAINT descriptors_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS descriptors_asoc (
    id INT AUTO_INCREMENT,
    artist_id INT NOT NULL,
    descriptor_id INT NOT NULL,
    descriptor_type VARCHAR(30) NOT NULL,
    CONSTRAINT descriptors_asoc_artist_id_fk FOREIGN KEY (artist_id) REFERENCES artist (id),
    CONSTRAINT descriptors_asoc_pk PRIMARY KEY (id)
);

CREATE INDEX descriptors_asoc_artist_id_descriptor_id_index ON descriptors_asoc (artist_id, descriptor_id);
CREATE INDEX descriptors_asoc_descriptor_type_index ON descriptors_asoc (descriptor_type);

CREATE TABLE IF NOT EXISTS friendship (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    friend_user_id INT NOT NULL,
    CONSTRAINT friendship_user_id_fk FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT friendship_friend_user_id_fk FOREIGN KEY (friend_user_id) REFERENCES users (id),
    CONSTRAINT friendship_pk PRIMARY KEY (id)
);

CREATE INDEX friendship_user_id_index ON friendship (user_id);

CREATE TABLE IF NOT EXISTS listen (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    artist_id INT NOT NULL,
    CONSTRAINT listen_artist_id_fk FOREIGN KEY (artist_id) REFERENCES artist (id),
    CONSTRAINT listen_user_id_fk FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT listen_pk PRIMARY KEY (id)
);

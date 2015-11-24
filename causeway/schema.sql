CREATE TABLE owner (
    address varchar(64) primary key,
    nonce varchar(32),
    balance integer,
    bad_attempts integer
);

CREATE TABLE kv (
    key varchar(64) primary key,
    value blob,
    owner varchar(64),
    sale_id integer,  /* which sale is this stored under */
    foreign key(owner) references owner(address)
);

CREATE TABLE wallet (
    address varchar(64) primary key,
    contact varchar(256),
    owner varchar(64)
);

CREATE TABLE sale (
    id integer primary key,
    owner varchar(64),
    created text,
    amount integer,
    term integer,
    price integer,
    foreign key(owner) references owner(address)
);

CREATE TABLE log (
    created text,
    ip varchar(45),  /* max length of ipv6 address */
    action varchar(10),
    bytes integer,
    owner varchar(64),
    message text,
    foreign key(owner) references owner(address)
);

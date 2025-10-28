CREATE TABLE guilds (
    id INTEGER PRIMARY KEY,
    guildid BIGINT NOT NULL UNIQUE,

    banned_users JSON NOT NULL DEFAULT('[]')
);

CREATE TABLE guild_permissions (
    guildid BIGINT NOT NULL UNIQUE PRIMARY KEY,
    ai BOOLEAN NOT NULL DEFAULT(TRUE),
    ai_channels JSON NOT NULL DEFAULT('[]'),

    FOREIGN KEY(guildid) REFERENCES guilds(guildid)
);

CREATE TABLE users (
    userid INTEGER PRIMARY KEY,
    role TEXT NOT NULL DEFAULT('user'),
    ai_banned BOOLEAN NOT NULL DEFAULT(FALSE)
);

CREATE TABLE facts (
    id INTEGER PRIMARY KEY,
    fact TEXT NOT NULL
);

-- Testing

-- INSERT INTO guilds(guildid) VALUES(1234);
-- INSERT INTO guild_permissions(guildid) VALUES(1234);


-- UPDATE guild_permissions
-- SET ai_channels = json_insert(
--     ai_channels,
--     '$[#]', 55743
-- )
-- WHERE guildid = 1234;

-- UPDATE guild_permissions
-- SET ai_channels = '[]'
-- WHERE guildid = 10

CREATE TABLE guilds (
    id INTEGER PRIMARY KEY,
    guildid BIGINT NOT NULL UNIQUE
);

CREATE TABLE guild_permissions (
    guildid BIGINT NOT NULL UNIQUE PRIMARY KEY,
    ai BOOLEAN NOT NULL DEFAULT(TRUE),
    ai_channels JSON NOT NULL DEFAULT('[]'),

    FOREIGN KEY(guildid) REFERENCES guilds(guildid)
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

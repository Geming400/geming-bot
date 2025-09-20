CREATE TABLE servers (
    id INTEGER PRIMARY KEY,
    serverid BIGINT NOT NULL UNIQUE
);

CREATE TABLE server_permissions (
    serverid BIGINT NOT NULL UNIQUE PRIMARY KEY,
    ai BOOLEAN NOT NULL DEFAULT(TRUE),
    ai_channels JSON NOT NULL DEFAULT('[]'),

    FOREIGN KEY(serverid) REFERENCES servers(serverid)
);

-- Testing

-- INSERT INTO servers(serverid) VALUES(1234);
-- INSERT INTO server_permissions(serverid) VALUES(1234);


-- UPDATE server_permissions
-- SET ai_channels = json_insert(
--     ai_channels,
--     '$[#]', 55743
-- )
-- WHERE serverid = 1234;

-- UPDATE server_permissions
-- SET ai_channels = '[]'
-- WHERE serverid = 10

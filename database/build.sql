CREATE TABLE IF NOT EXISTS exp (
    serverId BIGINT NOT NULL,
    UserID BIGINT NOT NULL,
    XP BIGINT DEFAULT 0,
    LVL INT DEFAULT 0,
    NextTextXpAt timestamp DEFAULT NOW()
);
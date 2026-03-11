import aiosqlite
from datetime import datetime
from config import DB_PATH


# ─────────────────────────────────────────────────────────────────
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                title       TEXT NOT NULL,
                category    TEXT NOT NULL,
                gift_link   TEXT NOT NULL,
                price       TEXT NOT NULL,
                currency    TEXT NOT NULL,
                description TEXT,
                contact     TEXT NOT NULL,
                status      TEXT DEFAULT 'active',
                views       INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_ads (
                user_id INTEGER,
                ad_id   INTEGER,
                PRIMARY KEY (user_id, ad_id)
            )
        """)
        await db.commit()


# ── Ads ──────────────────────────────────────────────────────────
async def create_ad(user_id, username, title, category, gift_link,
                    price, currency, description, contact) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO ads (user_id, username, title, category, gift_link,
                             price, currency, description, contact, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (user_id, username, title, category, gift_link,
              price, currency, description, contact,
              datetime.now().strftime("%Y-%m-%d %H:%M")))
        await db.commit()
        return cur.lastrowid


async def get_ad(ad_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM ads WHERE id=?", (ad_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_ads(category=None, page=0, per_page=5, status="active") -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if category:
            q = "SELECT * FROM ads WHERE status=? AND category=? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (status, category, per_page, page * per_page)
        else:
            q = "SELECT * FROM ads WHERE status=? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (status, per_page, page * per_page)
        async with db.execute(q, params) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_ads_count(category=None, status="active") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            async with db.execute(
                "SELECT COUNT(*) FROM ads WHERE status=? AND category=?", (status, category)
            ) as cur:
                return (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM ads WHERE status=?", (status,)
        ) as cur:
            return (await cur.fetchone())[0]


async def get_user_ads(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM ads WHERE user_id=? ORDER BY id DESC", (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def delete_ad(ad_id: int, user_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if user_id:
            await db.execute("DELETE FROM ads WHERE id=? AND user_id=?", (ad_id, user_id))
        else:
            await db.execute("DELETE FROM ads WHERE id=?", (ad_id,))
        await db.commit()


async def increment_views(ad_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE ads SET views=views+1 WHERE id=?", (ad_id,))
        await db.commit()


async def get_latest_ads(limit=5) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM ads WHERE status='active' ORDER BY id DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ── Saved ────────────────────────────────────────────────────────
async def save_ad(user_id: int, ad_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO saved_ads VALUES (?,?)", (user_id, ad_id)
            )
            await db.commit()
            return True
        except Exception:
            return False


async def get_saved_ads(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT a.* FROM ads a
            JOIN saved_ads s ON a.id=s.ad_id
            WHERE s.user_id=? AND a.status='active'
        """, (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ── Settings ─────────────────────────────────────────────────────
async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, value)
        )
        await db.commit()


async def get_setting(key: str, default=None) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default

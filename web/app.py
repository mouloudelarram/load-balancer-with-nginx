import os
import socket
import time

from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras


def _db_config():
    return {
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "appdb"),
        "user": os.getenv("DB_USER", "appuser"),
        "password": os.getenv("DB_PASSWORD", "apppass"),
    }


def get_conn():
    cfg = _db_config()
    return psycopg2.connect(**cfg)


def ensure_schema(max_wait_s: int = 30):
    deadline = time.time() + max_wait_s
    last_err = None
    while time.time() < deadline:
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS items (
                          id SERIAL PRIMARY KEY,
                          content TEXT NOT NULL,
                          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
            return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"DB not ready after {max_wait_s}s: {last_err}")


app = Flask(__name__)
ensure_schema()


@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503


@app.get("/")
def root():
    instance = socket.gethostname()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM items")
            count = cur.fetchone()[0]
    return jsonify({"instance": instance, "items_count": count})


@app.get("/items")
def list_items():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, content, created_at FROM items ORDER BY id DESC LIMIT 20"
            )
            rows = cur.fetchall()
    return jsonify({"items": rows})


@app.post("/items")
def create_item():
    payload = request.get_json(silent=True) or {}
    content = (payload.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Missing 'content'"}), 400

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO items (content) VALUES (%s) RETURNING id, content, created_at",
                (content,),
            )
            row = cur.fetchone()
    return jsonify(row), 201


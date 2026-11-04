"""
Dynamic Real-Time SQLite Warehouse & Inventory Engine for E-Commerce Swarm.
Tracks stock levels, unit economics, overstock status, and real-time depletions.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

DB_PATH = Path(__file__).resolve().parent / "warehouse.db"

# 20+ Real-world SKUs spanning 5 categories
INITIAL_INVENTORY_SEED = [
    # --- Category: Kitchen & Coffee ---
    {
        "sku": "COFFEE-MCH-01",
        "name": "BaristaPro Italian Espresso Machine",
        "category": "kitchen",
        "price": 280.00,
        "cogs": 110.00,
        "stock_units": 18,
        "is_overstock": 0,
        "weight_lbs": 14.5,
        "compatibility_tags": ["coffee", "kitchen", "espresso"]
    },
    {
        "sku": "COFFEE-BEAN-02",
        "name": "Artisan Single-Origin Ethiopian Roast (1kg)",
        "category": "kitchen",
        "price": 34.00,
        "cogs": 6.50,
        "stock_units": 340,
        "is_overstock": 1,
        "weight_lbs": 2.2,
        "compatibility_tags": ["coffee", "espresso"]
    },
    {
        "sku": "COFFEE-ACC-03",
        "name": "Precision Stainless Steel Calibrated Tamper",
        "category": "kitchen",
        "price": 28.00,
        "cogs": 5.00,
        "stock_units": 180,
        "is_overstock": 1,
        "weight_lbs": 1.1,
        "compatibility_tags": ["coffee", "espresso"]
    },
    {
        "sku": "COFFEE-SYRUP-04",
        "name": "Organic Madagascar Bourbon Vanilla Syrup (750ml)",
        "category": "kitchen",
        "price": 19.50,
        "cogs": 3.20,
        "stock_units": 215,
        "is_overstock": 1,
        "weight_lbs": 2.0,
        "compatibility_tags": ["coffee", "kitchen"]
    },
    {
        "sku": "KITCHEN-SCALE-05",
        "name": "Barista Dosing Digital Scale (0.1g Precision)",
        "category": "kitchen",
        "price": 32.00,
        "cogs": 7.50,
        "stock_units": 145,
        "is_overstock": 1,
        "weight_lbs": 0.9,
        "compatibility_tags": ["coffee", "kitchen", "espresso"]
    },

    # --- Category: Audio & Electronics ---
    {
        "sku": "AUDIO-NC-01",
        "name": "AcousticElite Wireless Noise-Cancelling Headphones",
        "category": "audio",
        "price": 220.00,
        "cogs": 85.00,
        "stock_units": 32,
        "is_overstock": 0,
        "weight_lbs": 1.2,
        "compatibility_tags": ["audio", "wireless", "music"]
    },
    {
        "sku": "AUDIO-CASE-02",
        "name": "Rugged Shockproof Ballistic Travel Case",
        "category": "audio",
        "price": 39.00,
        "cogs": 7.00,
        "stock_units": 260,
        "is_overstock": 1,
        "weight_lbs": 0.8,
        "compatibility_tags": ["audio", "travel", "wireless"]
    },
    {
        "sku": "AUDIO-CABLE-03",
        "name": "Gold-Plated Audiophile Braided Audio Cable",
        "category": "audio",
        "price": 24.00,
        "cogs": 3.50,
        "stock_units": 410,
        "is_overstock": 1,
        "weight_lbs": 0.4,
        "compatibility_tags": ["audio", "music"]
    },
    {
        "sku": "AUDIO-STAND-04",
        "name": "Brushed Aluminum Desktop Headphone Stand",
        "category": "audio",
        "price": 36.00,
        "cogs": 6.80,
        "stock_units": 175,
        "is_overstock": 1,
        "weight_lbs": 1.4,
        "compatibility_tags": ["audio", "desk"]
    },
    {
        "sku": "AUDIO-EARPAD-05",
        "name": "Cooling Gel Memory Foam Replacement Cushions",
        "category": "audio",
        "price": 26.00,
        "cogs": 4.20,
        "stock_units": 290,
        "is_overstock": 1,
        "weight_lbs": 0.3,
        "compatibility_tags": ["audio", "wireless", "music"]
    },

    # --- Category: Computing & Workstation ---
    {
        "sku": "KB-MECH-01",
        "name": "KeyCraft Pro Wireless Hot-Swap Mechanical Keyboard",
        "category": "computing",
        "price": 160.00,
        "cogs": 62.00,
        "stock_units": 25,
        "is_overstock": 0,
        "weight_lbs": 2.4,
        "compatibility_tags": ["computing", "desk", "keyboard"]
    },
    {
        "sku": "KB-REST-02",
        "name": "Ergonomic Walnut Hardwood Palm Rest",
        "category": "computing",
        "price": 35.00,
        "cogs": 6.00,
        "stock_units": 195,
        "is_overstock": 1,
        "weight_lbs": 0.9,
        "compatibility_tags": ["computing", "desk", "keyboard"]
    },
    {
        "sku": "DESK-MAT-03",
        "name": "Water-Resistant Felt Wool XXL Desk Mat (90x40cm)",
        "category": "computing",
        "price": 30.00,
        "cogs": 5.50,
        "stock_units": 310,
        "is_overstock": 1,
        "weight_lbs": 1.1,
        "compatibility_tags": ["computing", "desk", "keyboard", "monitor"]
    },
    {
        "sku": "CABLE-SPINE-04",
        "name": "Magnetic Under-Desk Cable Management Spine",
        "category": "computing",
        "price": 25.00,
        "cogs": 4.00,
        "stock_units": 225,
        "is_overstock": 1,
        "weight_lbs": 1.8,
        "compatibility_tags": ["computing", "desk"]
    },
    {
        "sku": "MONITOR-4K-01",
        "name": "UltraView 34-inch Curved QD-OLED Studio Monitor",
        "category": "computing",
        "price": 899.00,
        "cogs": 520.00,
        "stock_units": 9,
        "is_overstock": 0,
        "weight_lbs": 21.0,
        "compatibility_tags": ["computing", "monitor", "display"]
    },
    {
        "sku": "MONITOR-ARM-02",
        "name": "Heavy-Duty Gas Spring Articulating Monitor Arm",
        "category": "computing",
        "price": 75.00,
        "cogs": 18.00,
        "stock_units": 85,
        "is_overstock": 1,
        "weight_lbs": 6.5,
        "compatibility_tags": ["computing", "monitor", "desk"]
    },
    {
        "sku": "MONITOR-LIGHT-03",
        "name": "Anti-Glare ScreenBar LED Monitor Light Bar",
        "category": "computing",
        "price": 48.00,
        "cogs": 10.50,
        "stock_units": 160,
        "is_overstock": 1,
        "weight_lbs": 1.2,
        "compatibility_tags": ["computing", "monitor", "desk"]
    },

    # --- Category: Fitness & Workout ---
    {
        "sku": "FIT-ROWER-01",
        "name": "HydroPulse Smart Magnetic Resistance Home Rower",
        "category": "fitness",
        "price": 799.00,
        "cogs": 460.00,
        "stock_units": 12,
        "is_overstock": 0,
        "weight_lbs": 72.0,
        "compatibility_tags": ["fitness", "cardio", "workout"]
    },
    {
        "sku": "FIT-MAT-02",
        "name": "High-Density Shock Absorption Floor Equipment Mat",
        "category": "fitness",
        "price": 45.00,
        "cogs": 9.00,
        "stock_units": 180,
        "is_overstock": 1,
        "weight_lbs": 6.2,
        "compatibility_tags": ["fitness", "cardio", "workout"]
    },
    {
        "sku": "FIT-ELECTRO-03",
        "name": "Performance Hydration Electrolyte Pack (30 Servings)",
        "category": "fitness",
        "price": 22.00,
        "cogs": 3.80,
        "stock_units": 350,
        "is_overstock": 1,
        "weight_lbs": 1.0,
        "compatibility_tags": ["fitness", "workout", "cardio"]
    },
    {
        "sku": "FIT-ROLLER-04",
        "name": "Deep-Tissue Textured Trigger-Point Foam Roller",
        "category": "fitness",
        "price": 28.00,
        "cogs": 5.20,
        "stock_units": 230,
        "is_overstock": 1,
        "weight_lbs": 1.8,
        "compatibility_tags": ["fitness", "workout"]
    },

    # --- Category: Photography & Creator ---
    {
        "sku": "CAM-VLOG-01",
        "name": "CreatorPro 4K Vlogging Camera & Shotgun Mic Kit",
        "category": "photography",
        "price": 640.00,
        "cogs": 390.00,
        "stock_units": 15,
        "is_overstock": 0,
        "weight_lbs": 2.8,
        "compatibility_tags": ["photography", "video", "creator"]
    },
    {
        "sku": "CAM-STRAP-02",
        "name": "Quick-Release Neoprene Padded Pro Camera Strap",
        "category": "photography",
        "price": 32.00,
        "cogs": 5.50,
        "stock_units": 190,
        "is_overstock": 1,
        "weight_lbs": 0.4,
        "compatibility_tags": ["photography", "creator"]
    },
    {
        "sku": "CAM-CLEAN-03",
        "name": "Optics Cleaning Pen & Multi-Coated UV Lens Filter",
        "category": "photography",
        "price": 25.00,
        "cogs": 3.90,
        "stock_units": 280,
        "is_overstock": 1,
        "weight_lbs": 0.3,
        "compatibility_tags": ["photography", "video", "creator"]
    }
]


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with WAL mode enabled for concurrent access."""
    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def init_warehouse_db(force_reseed: bool = False):
    """Initializes tables and seeds initial catalog if not present."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                cogs REAL NOT NULL,
                stock_units INTEGER NOT NULL,
                is_overstock INTEGER NOT NULL,
                weight_lbs REAL NOT NULL,
                compatibility_tags TEXT NOT NULL,
                times_bundled INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                previous_stock INTEGER NOT NULL,
                new_stock INTEGER NOT NULL,
                cart_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        # Check existing row count
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM inventory;")
        count = cursor.fetchone()["cnt"]

        if count == 0 or force_reseed:
            if force_reseed:
                conn.execute("DELETE FROM inventory;")
            for item in INITIAL_INVENTORY_SEED:
                tags_str = json.dumps(item["compatibility_tags"])
                conn.execute("""
                    INSERT OR REPLACE INTO inventory 
                    (sku, name, category, price, cogs, stock_units, is_overstock, weight_lbs, compatibility_tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    item["sku"], item["name"], item["category"], item["price"],
                    item["cogs"], item["stock_units"], item["is_overstock"],
                    item["weight_lbs"], tags_str
                ))
            conn.commit()


def query_overstock_complements(category: str, compatibility_tag: str) -> List[Dict[str, Any]]:
    """
    Real-time warehouse query for high-margin clearance accessories.
    Ensures stock_units > 0 and calculates live gross margin.
    """
    init_warehouse_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT sku, name, category, price, cogs, stock_units, is_overstock, weight_lbs, compatibility_tags
            FROM inventory
            WHERE is_overstock = 1 AND stock_units > 0 AND category = ?;
        """, (category.lower(),))
        rows = cursor.fetchall()

    matches = []
    tag_clean = compatibility_tag.lower().strip()
    for row in rows:
        tags = json.loads(row["compatibility_tags"])
        tags_lower = [t.lower() for t in tags]
        # Match if tag is in compatibility list or if general fallback
        if tag_clean in tags_lower or "general" in tags_lower or not tag_clean:
            margin_pct = round(((row["price"] - row["cogs"]) / row["price"]) * 100, 1)
            matches.append({
                "sku": row["sku"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "cogs": row["cogs"],
                "margin_pct": margin_pct,
                "units_in_stock": row["stock_units"],
                "weight_lbs": row["weight_lbs"],
                "compatibility_tags": tags,
                "description": f"Live clearance stock: {row['name']} ({margin_pct}% margin, {row['stock_units']} units on hand)"
            })

    # Sort descending by margin percentage
    matches.sort(key=lambda x: x["margin_pct"], reverse=True)
    return matches


def get_product(sku: str) -> Optional[Dict[str, Any]]:
    """Retrieves real-time SKU details from SQLite."""
    init_warehouse_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT sku, name, category, price, cogs, stock_units, is_overstock, weight_lbs, compatibility_tags
            FROM inventory WHERE sku = ?;
        """, (sku.upper(),))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "sku": row["sku"],
            "name": row["name"],
            "category": row["category"],
            "price": row["price"],
            "cogs": row["cogs"],
            "stock_units": row["stock_units"],
            "is_overstock": bool(row["is_overstock"]),
            "weight_lbs": row["weight_lbs"],
            "compatibility_tags": json.loads(row["compatibility_tags"])
        }


def deplete_stock(sku: str, quantity: int = 1, cart_id: str = "") -> Dict[str, Any]:
    """
    Real-time inventory deduction when an agent recovery offer is dispatched.
    Automatically turns off overstock flag if stock drops below healthy reserve.
    """
    init_warehouse_db()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT stock_units, is_overstock, name, category FROM inventory WHERE sku = ?;", (sku.upper(),))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": f"SKU {sku} not found."}

        prev_stock = row["stock_units"]
        new_stock = max(0, prev_stock - quantity)
        
        # If stock drops to 20 or below, it is no longer in excess overstock
        new_is_overstock = 1 if (new_stock > 20 and row["is_overstock"]) else 0

        conn.execute("""
            UPDATE inventory 
            SET stock_units = ?, 
                times_bundled = times_bundled + ?,
                is_overstock = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE sku = ?;
        """, (new_stock, quantity, new_is_overstock, sku.upper()))

        conn.execute("""
            INSERT INTO inventory_audit_log (sku, action, quantity, previous_stock, new_stock, cart_id)
            VALUES (?, 'DEPLETED', ?, ?, ?, ?);
        """, (sku.upper(), quantity, prev_stock, new_stock, cart_id))
        conn.commit()

        return {
            "success": True,
            "sku": sku.upper(),
            "name": row["name"],
            "category": row["category"],
            "previous_stock": prev_stock,
            "remaining_stock": new_stock,
            "is_overstock": bool(new_is_overstock)
        }


def list_inventory_status() -> List[Dict[str, Any]]:
    """Returns a full inventory snapshot for telemetry and reporting."""
    init_warehouse_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT sku, name, category, price, cogs, stock_units, is_overstock, times_bundled
            FROM inventory
            ORDER BY category ASC, is_overstock DESC, stock_units DESC;
        """)
        return [dict(r) for r in cursor.fetchall()]

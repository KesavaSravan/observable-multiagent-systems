"""
E-Commerce Product Catalog, Warehouse Inventory, and Abandoned Cart Presets.
Expanded with 20+ realistic products across 5 categories.
"""

from typing import Dict, List, Any

# Product Catalog with real unit economics (COGS, Stock Level, Overstock flag)
PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    # --- Category: Kitchen & Coffee ---
    "COFFEE-MCH-01": {
        "sku": "COFFEE-MCH-01",
        "name": "BaristaPro Italian Espresso Machine",
        "category": "kitchen",
        "price": 280.00,
        "cogs": 110.00,
        "stock": 18,
        "is_overstock": False,
        "weight_lbs": 14.5,
        "compatibility_tags": ["coffee", "kitchen", "espresso"]
    },
    "COFFEE-BEAN-02": {
        "sku": "COFFEE-BEAN-02",
        "name": "Artisan Single-Origin Ethiopian Roast (1kg)",
        "category": "kitchen",
        "price": 34.00,
        "cogs": 6.50, # 80.9% gross margin
        "stock": 340,
        "is_overstock": True,
        "weight_lbs": 2.2,
        "compatibility_tags": ["coffee", "espresso"]
    },
    "COFFEE-ACC-03": {
        "sku": "COFFEE-ACC-03",
        "name": "Precision Stainless Steel Calibrated Tamper",
        "category": "kitchen",
        "price": 28.00,
        "cogs": 5.00, # 82.1% margin
        "stock": 180,
        "is_overstock": True,
        "weight_lbs": 1.1,
        "compatibility_tags": ["coffee", "espresso"]
    },
    "COFFEE-SYRUP-04": {
        "sku": "COFFEE-SYRUP-04",
        "name": "Organic Madagascar Bourbon Vanilla Syrup (750ml)",
        "category": "kitchen",
        "price": 19.50,
        "cogs": 3.20,
        "stock": 215,
        "is_overstock": True,
        "weight_lbs": 2.0,
        "compatibility_tags": ["coffee", "kitchen"]
    },
    "KITCHEN-SCALE-05": {
        "sku": "KITCHEN-SCALE-05",
        "name": "Barista Dosing Digital Scale (0.1g Precision)",
        "category": "kitchen",
        "price": 32.00,
        "cogs": 7.50,
        "stock": 145,
        "is_overstock": True,
        "weight_lbs": 0.9,
        "compatibility_tags": ["coffee", "kitchen", "espresso"]
    },

    # --- Category: Audio & Electronics ---
    "AUDIO-NC-01": {
        "sku": "AUDIO-NC-01",
        "name": "AcousticElite Wireless Noise-Cancelling Headphones",
        "category": "audio",
        "price": 220.00,
        "cogs": 85.00,
        "stock": 32,
        "is_overstock": False,
        "weight_lbs": 1.2,
        "compatibility_tags": ["audio", "wireless", "music"]
    },
    "AUDIO-CASE-02": {
        "sku": "AUDIO-CASE-02",
        "name": "Rugged Shockproof Ballistic Travel Case",
        "category": "audio",
        "price": 39.00,
        "cogs": 7.00, # 82% margin
        "stock": 260,
        "is_overstock": True,
        "weight_lbs": 0.8,
        "compatibility_tags": ["audio", "travel", "wireless"]
    },
    "AUDIO-CABLE-03": {
        "sku": "AUDIO-CABLE-03",
        "name": "Gold-Plated Audiophile Braided Audio Cable",
        "category": "audio",
        "price": 24.00,
        "cogs": 3.50, # 85.4% margin
        "stock": 410,
        "is_overstock": True,
        "weight_lbs": 0.4,
        "compatibility_tags": ["audio", "music"]
    },
    "AUDIO-STAND-04": {
        "sku": "AUDIO-STAND-04",
        "name": "Brushed Aluminum Desktop Headphone Stand",
        "category": "audio",
        "price": 36.00,
        "cogs": 6.80,
        "stock": 175,
        "is_overstock": True,
        "weight_lbs": 1.4,
        "compatibility_tags": ["audio", "desk"]
    },
    "AUDIO-EARPAD-05": {
        "sku": "AUDIO-EARPAD-05",
        "name": "Cooling Gel Memory Foam Replacement Cushions",
        "category": "audio",
        "price": 26.00,
        "cogs": 4.20,
        "stock": 290,
        "is_overstock": True,
        "weight_lbs": 0.3,
        "compatibility_tags": ["audio", "wireless", "music"]
    },

    # --- Category: Computing & Workstation ---
    "KB-MECH-01": {
        "sku": "KB-MECH-01",
        "name": "KeyCraft Pro Wireless Hot-Swap Mechanical Keyboard",
        "category": "computing",
        "price": 160.00,
        "cogs": 62.00,
        "stock": 25,
        "is_overstock": False,
        "weight_lbs": 2.4,
        "compatibility_tags": ["computing", "desk", "keyboard"]
    },
    "KB-REST-02": {
        "sku": "KB-REST-02",
        "name": "Ergonomic Walnut Hardwood Palm Rest",
        "category": "computing",
        "price": 35.00,
        "cogs": 6.00, # 82.9% margin
        "stock": 195,
        "is_overstock": True,
        "weight_lbs": 0.9,
        "compatibility_tags": ["computing", "desk", "keyboard"]
    },
    "DESK-MAT-03": {
        "sku": "DESK-MAT-03",
        "name": "Water-Resistant Felt Wool XXL Desk Mat (90x40cm)",
        "category": "computing",
        "price": 30.00,
        "cogs": 5.50, # 81.7% margin
        "stock": 310,
        "is_overstock": True,
        "weight_lbs": 1.1,
        "compatibility_tags": ["computing", "desk", "keyboard", "monitor"]
    },
    "CABLE-SPINE-04": {
        "sku": "CABLE-SPINE-04",
        "name": "Magnetic Under-Desk Cable Management Spine",
        "category": "computing",
        "price": 25.00,
        "cogs": 4.00,
        "stock": 225,
        "is_overstock": True,
        "weight_lbs": 1.8,
        "compatibility_tags": ["computing", "desk"]
    },
    "MONITOR-4K-01": {
        "sku": "MONITOR-4K-01",
        "name": "UltraView 34-inch Curved QD-OLED Studio Monitor",
        "category": "computing",
        "price": 899.00,
        "cogs": 520.00,
        "stock": 9,
        "is_overstock": False,
        "weight_lbs": 21.0,
        "compatibility_tags": ["computing", "monitor", "display"]
    },
    "MONITOR-ARM-02": {
        "sku": "MONITOR-ARM-02",
        "name": "Heavy-Duty Gas Spring Articulating Monitor Arm",
        "category": "computing",
        "price": 75.00,
        "cogs": 18.00, # 76% margin
        "stock": 85,
        "is_overstock": True,
        "weight_lbs": 6.5,
        "compatibility_tags": ["computing", "monitor", "desk"]
    },
    "MONITOR-LIGHT-03": {
        "sku": "MONITOR-LIGHT-03",
        "name": "Anti-Glare ScreenBar LED Monitor Light Bar",
        "category": "computing",
        "price": 48.00,
        "cogs": 10.50,
        "stock": 160,
        "is_overstock": True,
        "weight_lbs": 1.2,
        "compatibility_tags": ["computing", "monitor", "desk"]
    },

    # --- Category: Fitness & Workout ---
    "FIT-ROWER-01": {
        "sku": "FIT-ROWER-01",
        "name": "HydroPulse Smart Magnetic Resistance Home Rower",
        "category": "fitness",
        "price": 799.00,
        "cogs": 460.00,
        "stock": 12,
        "is_overstock": False,
        "weight_lbs": 72.0,
        "compatibility_tags": ["fitness", "cardio", "workout"]
    },
    "FIT-MAT-02": {
        "sku": "FIT-MAT-02",
        "name": "High-Density Shock Absorption Floor Equipment Mat",
        "category": "fitness",
        "price": 45.00,
        "cogs": 9.00, # 80% margin
        "stock": 180,
        "is_overstock": True,
        "weight_lbs": 6.2,
        "compatibility_tags": ["fitness", "cardio", "workout"]
    },
    "FIT-ELECTRO-03": {
        "sku": "FIT-ELECTRO-03",
        "name": "Performance Hydration Electrolyte Pack (30 Servings)",
        "category": "fitness",
        "price": 22.00,
        "cogs": 3.80,
        "stock": 350,
        "is_overstock": True,
        "weight_lbs": 1.0,
        "compatibility_tags": ["fitness", "workout", "cardio"]
    },
    "FIT-ROLLER-04": {
        "sku": "FIT-ROLLER-04",
        "name": "Deep-Tissue Textured Trigger-Point Foam Roller",
        "category": "fitness",
        "price": 28.00,
        "cogs": 5.20,
        "stock": 230,
        "is_overstock": True,
        "weight_lbs": 1.8,
        "compatibility_tags": ["fitness", "workout"]
    },

    # --- Category: Photography & Creator ---
    "CAM-VLOG-01": {
        "sku": "CAM-VLOG-01",
        "name": "CreatorPro 4K Vlogging Camera & Shotgun Mic Kit",
        "category": "photography",
        "price": 640.00,
        "cogs": 390.00,
        "stock": 15,
        "is_overstock": False,
        "weight_lbs": 2.8,
        "compatibility_tags": ["photography", "video", "creator"]
    },
    "CAM-STRAP-02": {
        "sku": "CAM-STRAP-02",
        "name": "Quick-Release Neoprene Padded Pro Camera Strap",
        "category": "photography",
        "price": 32.00,
        "cogs": 5.50, # 82.8% margin
        "stock": 190,
        "is_overstock": True,
        "weight_lbs": 0.4,
        "compatibility_tags": ["photography", "creator"]
    },
    "CAM-CLEAN-03": {
        "sku": "CAM-CLEAN-03",
        "name": "Optics Cleaning Pen & Multi-Coated UV Lens Filter",
        "category": "photography",
        "price": 25.00,
        "cogs": 3.90, # 84.4% margin
        "stock": 280,
        "is_overstock": True,
        "weight_lbs": 0.3,
        "compatibility_tags": ["photography", "video", "creator"]
    }
}


# Realistic Abandoned Cart Presets Across Multiple Categories
ABANDONED_CART_PRESETS: List[Dict[str, Any]] = [
    {
        "cart_id": "CART-7891",
        "customer_name": "Marcus Vance",
        "customer_email": "marcus.v@example.com",
        "customer_tier": "REPEAT",
        "cart_items": [PRODUCT_CATALOG["COFFEE-MCH-01"]],
        "checkout_dwell_seconds": 215,
        "exit_point": "shipping_calculator",
        "shipping_quote_usd": 24.50,
        "description": "Left espresso machine at shipping calculator after seeing $24.50 freight cost."
    },
    {
        "cart_id": "CART-3420",
        "customer_name": "Sarah Chen",
        "customer_email": "sarah.c@example.com",
        "customer_tier": "FIRST_TIME",
        "cart_items": [PRODUCT_CATALOG["AUDIO-NC-01"]],
        "checkout_dwell_seconds": 380,
        "exit_point": "payment_step",
        "shipping_quote_usd": 0.0,
        "description": "Price hesitation at final payment screen for wireless headphones."
    },
    {
        "cart_id": "CART-9102",
        "customer_name": "David Miller",
        "customer_email": "david.m@example.com",
        "customer_tier": "VIP",
        "cart_items": [PRODUCT_CATALOG["KB-MECH-01"]],
        "checkout_dwell_seconds": 90,
        "exit_point": "cart_view",
        "shipping_quote_usd": 8.0,
        "description": "VIP buyer hesitated on mechanical keyboard without palm rest or mat."
    },
    {
        "cart_id": "CART-5511",
        "customer_name": "Elena Rostova",
        "customer_email": "elena.r@example.com",
        "customer_tier": "FIRST_TIME",
        "cart_items": [PRODUCT_CATALOG["MONITOR-4K-01"]],
        "checkout_dwell_seconds": 450,
        "exit_point": "payment_step",
        "shipping_quote_usd": 35.0,
        "description": "High-ticket $899 OLED monitor abandoned; requires Merchandiser HITL review."
    },
    {
        "cart_id": "CART-6622",
        "customer_name": "Tyler Brooks",
        "customer_email": "tyler.b@example.com",
        "customer_tier": "REPEAT",
        "cart_items": [PRODUCT_CATALOG["FIT-ROWER-01"]],
        "checkout_dwell_seconds": 310,
        "exit_point": "shipping_calculator",
        "shipping_quote_usd": 65.0,
        "description": "Home fitness rower abandoned due to high freight delivery cost ($65.00)."
    },
    {
        "cart_id": "CART-8833",
        "customer_name": "Chloe Bennett",
        "customer_email": "chloe.b@example.com",
        "customer_tier": "FIRST_TIME",
        "cart_items": [PRODUCT_CATALOG["CAM-VLOG-01"]],
        "checkout_dwell_seconds": 290,
        "exit_point": "payment_step",
        "shipping_quote_usd": 12.0,
        "description": "Content creator abandoned 4K Vlogging Kit at payment step."
    }
]

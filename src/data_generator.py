"""
Lorem ipsum POS data generator.

Generates 2 years (2023-2024) of realistic transaction data for
Burger Joint Center, Ljubljana — with outdoor terrace.

Patterns:
- Lunch peak: 12-14h, dinner peak: 18-20h
- Weekdays: ~300-350 burgers/day, weekends: ~400-450 burgers/day
- Weather impact: rain -20%, hot sunny (>25°C) +15% (terrace effect)
- Special event spikes: New Year, Pustovanje, Ljubljana Marathon, summer festival
- Bun waste: over-ordering by 8-12% every day (the problem we're solving)
"""

import random
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# Static data
# ---------------------------------------------------------------------------

def generate_locations():
    """Return the single Ljubljana center location."""
    return [
        {
            'name': 'Burger Joint Center',
            'address': 'Kongresni trg 3, 1000 Ljubljana',
            'latitude': 46.0511,
            'longitude': 14.5051,
            'has_terrace': True,
            'opened_date': datetime(2021, 4, 1),
        }
    ]


def generate_menu_items():
    """Return the full menu grouped by category."""
    return {
        'burgers': [
            {'name': 'Classic Burger',  'price': 6.50},
            {'name': 'Cheeseburger',    'price': 7.00},
            {'name': 'Bacon Deluxe',    'price': 8.50},
            {'name': 'Veggie Burger',   'price': 7.00},
            {'name': 'Chicken Burger',  'price': 7.50},
        ],
        'sides': [
            {'name': 'French Fries',    'price': 2.50},
            {'name': 'Onion Rings',     'price': 3.00},
            {'name': 'Side Salad',      'price': 3.50},
            {'name': 'Coleslaw',        'price': 2.00},
        ],
        'drinks': [
            {'name': 'Coca Cola',       'price': 2.00},
            {'name': 'Beer (0.5L)',     'price': 3.50},
            {'name': 'Water',           'price': 1.50},
            {'name': 'Coffee',          'price': 1.80},
        ],
        'desserts': [
            {'name': 'Ice Cream',       'price': 2.50},
            {'name': 'Brownie',         'price': 3.00},
        ],
    }


# ---------------------------------------------------------------------------
# Special events: date → sales multiplier
# One bun per burger, so events also spike bun usage.
# ---------------------------------------------------------------------------

SPECIAL_EVENTS = {
    # 2022
    date(2022, 1, 1):  1.8,   # New Year's Day
    date(2022, 3, 1):  1.4,   # Pustovanje 2022 (Mardi Gras)
    date(2022, 7, 5):  1.3,   # Summer festival on Congress Square
    date(2022, 7, 6):  1.3,
    date(2022, 7, 7):  1.3,
    date(2022, 10, 23): 1.5,  # Ljubljana Marathon 2022
    date(2022, 12, 31): 1.6,  # New Year's Eve

    # 2023
    date(2023, 1, 1):  1.8,
    date(2023, 2, 21): 1.4,   # Pustovanje 2023
    date(2023, 7, 4):  1.3,   # Summer festival on Congress Square
    date(2023, 7, 5):  1.3,
    date(2023, 7, 6):  1.3,
    date(2023, 10, 29): 1.5,  # Ljubljana Marathon 2023
    date(2023, 12, 31): 1.6,

    # 2024
    date(2024, 1, 1):  1.8,
    date(2024, 2, 13): 1.4,   # Pustovanje 2024
    date(2024, 7, 2):  1.3,   # Summer festival on Congress Square
    date(2024, 7, 3):  1.3,
    date(2024, 7, 4):  1.3,
    date(2024, 10, 27): 1.5,  # Ljubljana Marathon 2024
    date(2024, 12, 31): 1.6,

    # 2025
    date(2025, 1, 1):  1.8,
    date(2025, 3, 4):  1.4,   # Pustovanje 2025
    date(2025, 7, 1):  1.3,   # Summer festival on Congress Square
    date(2025, 7, 2):  1.3,
    date(2025, 7, 3):  1.3,
    date(2025, 10, 19): 1.5,  # Ljubljana Marathon 2025
    date(2025, 12, 31): 1.6,
}

# Hourly traffic weights (restaurant open 9-22h, sums to 1.0)
HOUR_WEIGHTS = {
    9: 0.01, 10: 0.02, 11: 0.07,
    12: 0.15, 13: 0.15, 14: 0.08,
    15: 0.05, 16: 0.05, 17: 0.07,
    18: 0.12, 19: 0.12, 20: 0.07,
    21: 0.03, 22: 0.01,
}
_HOURS = list(HOUR_WEIGHTS.keys())
_WEIGHTS = list(HOUR_WEIGHTS.values())

PAYMENT_METHODS = ['card', 'cash', 'online']
PAYMENT_WEIGHTS = [60, 30, 10]

CATEGORY_MAP = {
    'burgers': 'burger',
    'sides':   'side',
    'drinks':  'drink',
    'desserts': 'dessert',
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pick_hour():
    """Pick a transaction hour based on realistic traffic weights."""
    return random.choices(_HOURS, weights=_WEIGHTS, k=1)[0]


def _make_timestamp(day, hour):
    """Build a datetime for a given day and hour with random minutes/seconds."""
    return datetime(day.year, day.month, day.day,
                    hour,
                    random.randint(0, 59),
                    random.randint(0, 59))


def _generate_order_items(burgers, sides, drinks, desserts):
    """
    Generate order items for one transaction.
    Returns (list_of_dicts, burger_count).
    Each dict has: item_id, quantity, unit_price, total_price.
    """
    items = []
    burger_count = 0

    # Burgers — always at least 1
    num_burgers = random.choices([1, 2, 3], weights=[55, 35, 10], k=1)[0]
    for _ in range(num_burgers):
        b = random.choice(burgers)
        items.append({
            'item_id': b.id,
            'quantity': 1,
            'unit_price': b.base_price,
            'total_price': b.base_price,
        })
        burger_count += 1

    # Sides — 70% chance
    if random.random() < 0.70:
        num_sides = random.choices([1, 2], weights=[75, 25], k=1)[0]
        for _ in range(num_sides):
            s = random.choice(sides)
            items.append({
                'item_id': s.id,
                'quantity': 1,
                'unit_price': s.base_price,
                'total_price': s.base_price,
            })

    # Drinks — 60% chance
    if random.random() < 0.60:
        d = random.choice(drinks)
        items.append({
            'item_id': d.id,
            'quantity': 1,
            'unit_price': d.base_price,
            'total_price': d.base_price,
        })

    # Dessert — 15% chance
    if random.random() < 0.15:
        des = random.choice(desserts)
        items.append({
            'item_id': des.id,
            'quantity': 1,
            'unit_price': des.base_price,
            'total_price': des.base_price,
        })

    return items, burger_count


_GROWTH_BASE_YEAR = 2022
_ANNUAL_GROWTH    = 0.06   # 6% more transactions per year — restaurant is growing


def _daily_transaction_count(day, weather_conditions, weather_temp):
    """
    Compute target transaction count for a day.
    Base (2022): weekday ~185 txns, weekend ~242 txns.

    Multipliers applied:
      - Weather:    rain/snow -20%, hot sunny +15%
      - Events:     special days (marathons, festivals, New Year)
      - Growth:     +6% per year vs 2022 base (restaurant is growing)
      - Bad day:    ~1x/year a random -40 to -70% hit (equipment, staff, etc.)
    """
    is_weekend = day.weekday() >= 5
    if is_weekend:
        base = random.randint(222, 250)
    else:
        base = random.randint(167, 194)

    # Weather
    weather_mult = 1.0
    if weather_conditions in ('Rain', 'Thunderstorm', 'Snow', 'Drizzle'):
        weather_mult = 0.80
    elif weather_conditions == 'Clear' and weather_temp is not None and weather_temp > 25:
        weather_mult = 1.15

    # Event
    event_mult = SPECIAL_EVENTS.get(day, 1.0)

    # Growth trend — compound 6% per year from 2022 baseline
    growth_mult = (1 + _ANNUAL_GROWTH) ** (day.year - _GROWTH_BASE_YEAR)

    # Rare bad day: equipment failure, staff sick, unexpected issue (~1 per year)
    bad_day_mult = 1.0
    if random.random() < 0.003:
        bad_day_mult = random.uniform(0.30, 0.60)

    return max(10, int(base * weather_mult * event_mult * growth_mult * bad_day_mult))


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def generate_transactions(location, start_date, end_date,
                          menu_items_by_category, weather_by_date, session):
    """
    Generate all transactions for the location over the date range.
    Inserts Transaction, OrderItem, and DailyBunRecord rows into the DB.

    Args:
        location:               SQLAlchemy Location object (already in DB)
        start_date:             date object
        end_date:               date object (inclusive)
        menu_items_by_category: dict {'burger': [...], 'side': [...], ...}
                                with SQLAlchemy MenuItem objects
        weather_by_date:        dict {date: WeatherSnapshot} (may be empty)
        session:                SQLAlchemy session
    """
    from src.db_models import Transaction, OrderItem, DailyBunRecord

    burgers  = menu_items_by_category['burger']
    sides    = menu_items_by_category['side']
    drinks   = menu_items_by_category['drink']
    desserts = menu_items_by_category['dessert']

    current = start_date
    total_days = (end_date - start_date).days + 1
    day_index = 0

    while current <= end_date:
        # Weather for today (may be None if not available)
        snap = weather_by_date.get(current)
        weather_cond = snap.conditions if snap else 'Clear'
        weather_temp = snap.temperature if snap else None
        snap_id = snap.id if snap else None

        num_transactions = _daily_transaction_count(current, weather_cond, weather_temp)

        # --- Build Transaction ORM objects ---
        day_transactions = []
        for _ in range(num_transactions):
            hour = _pick_hour()
            ts = _make_timestamp(current, hour)
            payment = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0]
            day_transactions.append(Transaction(
                location_id=location.id,
                timestamp=ts,
                total_amount=0.0,  # will update after items are known
                payment_method=payment,
                weather_snapshot_id=snap_id,
            ))

        session.add_all(day_transactions)
        session.flush()  # assigns IDs

        # --- Build OrderItem dicts + compute totals ---
        order_item_dicts = []
        daily_burger_count = 0

        for t in day_transactions:
            items, burger_count = _generate_order_items(burgers, sides, drinks, desserts)
            daily_burger_count += burger_count
            total = sum(i['total_price'] for i in items)
            t.total_amount = round(total, 2)

            for item in items:
                order_item_dicts.append({
                    'transaction_id': t.id,
                    'item_id':    item['item_id'],
                    'quantity':   item['quantity'],
                    'unit_price': item['unit_price'],
                    'total_price': item['total_price'],
                })

        session.bulk_insert_mappings(OrderItem, order_item_dicts)

        # --- Bun waste record ---
        over_order_rate = random.uniform(0.08, 0.12)
        ordered_buns = int(daily_burger_count * (1 + over_order_rate))
        waste_pct = round((ordered_buns - daily_burger_count) / ordered_buns * 100, 2)

        session.add(DailyBunRecord(
            location_id=location.id,
            date=current,
            ordered_buns=ordered_buns,
            actual_buns_used=daily_burger_count,
            waste_percentage=waste_pct,
        ))

        session.commit()

        day_index += 1
        if day_index % 60 == 0 or day_index == total_days:
            pct = round(day_index / total_days * 100)
            print(f"  Generating transactions... {day_index}/{total_days} days ({pct}%)")

        current += timedelta(days=1)

    print(f"  Done: {total_days} days generated.")


# ---------------------------------------------------------------------------
# Seed orchestrator
# ---------------------------------------------------------------------------

def seed_database(db_path='data/demo_pos_data.db',
                  start_date=date(2022, 1, 1),
                  end_date=date(2025, 12, 31)):
    """
    Full database seed:
    1. Create location
    2. Create menu items
    3. Fetch real weather from Open-Meteo (free, no API key)
    4. Generate transactions + bun waste records

    Args:
        db_path:    Path to SQLite file
        start_date: First day of data
        end_date:   Last day of data (inclusive)
    """
    import os
    from src.db_models import init_db, get_session, Location, MenuItem, WeatherSnapshot

    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else 'data', exist_ok=True)
    os.makedirs('data/weather_cache', exist_ok=True)

    engine = init_db(db_path)
    session = get_session(engine)

    # ---- 1. Location -------------------------------------------------------
    location = session.query(Location).first()
    if not location:
        loc_data = generate_locations()[0]
        location = Location(**loc_data)
        session.add(location)
        session.commit()
        print(f"[1/4] Location created: {location.name}")
    else:
        print(f"[1/4] Location exists: {location.name}")

    # ---- 2. Menu items -----------------------------------------------------
    if session.query(MenuItem).count() == 0:
        menu = generate_menu_items()
        for cat_key, items in menu.items():
            category = CATEGORY_MAP[cat_key]
            for item in items:
                session.add(MenuItem(
                    name=item['name'],
                    category=category,
                    base_price=item['price'],
                ))
        session.commit()
        print(f"[2/4] Menu seeded: {session.query(MenuItem).count()} items")
    else:
        print(f"[2/4] Menu exists: {session.query(MenuItem).count()} items")

    # ---- 3. Weather --------------------------------------------------------
    if session.query(WeatherSnapshot).count() == 0:
        from src.weather import fetch_and_store_weather
        print("[3/4] Fetching real weather from Open-Meteo (free, no API key) ...")
        fetch_and_store_weather(session, location, start_date, end_date)
        session.commit()
        print(f"      Weather records: {session.query(WeatherSnapshot).count()}")
    else:
        print(f"[3/4] Weather exists: {session.query(WeatherSnapshot).count()} records")

    # Build date → snapshot lookup for transaction generation
    snapshots = session.query(WeatherSnapshot).filter(
        WeatherSnapshot.location_id == location.id
    ).all()
    weather_by_date = {s.timestamp.date(): s for s in snapshots}

    # ---- 4. Transactions + bun records ------------------------------------
    from src.db_models import Transaction
    if session.query(Transaction).count() == 0:
        menu_items = session.query(MenuItem).all()
        menu_by_cat = {
            'burger':  [m for m in menu_items if m.category == 'burger'],
            'side':    [m for m in menu_items if m.category == 'side'],
            'drink':   [m for m in menu_items if m.category == 'drink'],
            'dessert': [m for m in menu_items if m.category == 'dessert'],
        }
        print("[4/4] Generating 4 years of transactions ...")
        generate_transactions(location, start_date, end_date, menu_by_cat, weather_by_date, session)
        total_txn = session.query(Transaction).count()
        print(f"      Transactions: {total_txn:,}")
    else:
        print(f"[4/4] Transactions exist: {session.query(Transaction).count():,}")

    session.close()
    print("\nSeed complete.")
    return engine

"""
Database models for burger analytics dashboard.

Tables:
- locations: Ljubljana burger joint location(s)
- transactions: Individual customer orders
- order_items: Line items for each transaction
- menu_items: Burger menu (burgers, fries, drinks, sides)
- weather_snapshots: Daily weather data for correlation analysis
- daily_bun_records: Per-day bun ordering vs usage (waste tracking)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    has_terrace = Column(Boolean, default=False)
    opened_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="location")
    weather_snapshots = relationship("WeatherSnapshot", back_populates="location")
    daily_bun_records = relationship("DailyBunRecord", back_populates="location")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String)  # cash, card, online
    weather_snapshot_id = Column(Integer, ForeignKey('weather_snapshots.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="transactions")
    order_items = relationship("OrderItem", back_populates="transaction")
    weather_snapshot = relationship("WeatherSnapshot")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="order_items")
    menu_item = relationship("MenuItem")


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # burger, side, drink, dessert
    base_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeatherSnapshot(Base):
    __tablename__ = 'weather_snapshots'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)  # daily snapshot at noon
    temperature = Column(Float)   # °C
    precipitation = Column(Float) # mm
    conditions = Column(String)   # Clear, Rain, Snow, Clouds, Thunderstorm, Fog
    wind_speed = Column(Float)    # m/s
    humidity = Column(Integer)    # %
    source = Column(String, default='synthetic')  # 'synthetic' or 'openweathermap'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="weather_snapshots")


class DailyBunRecord(Base):
    """
    Per-day bun waste tracking.
    Shows how many buns were ordered vs actually used.
    This is the problem we are solving: over-ordering by 8-12% every day.
    """
    __tablename__ = 'daily_bun_records'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    date = Column(Date, nullable=False)
    ordered_buns = Column(Integer, nullable=False)      # what was ordered from supplier
    actual_buns_used = Column(Integer, nullable=False)  # burgers sold that day
    waste_percentage = Column(Float, nullable=False)    # (ordered - used) / ordered * 100
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="daily_bun_records")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def init_db(db_path='data/demo_pos_data.db'):
    """Initialize database and create all tables."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()

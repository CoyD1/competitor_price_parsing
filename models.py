from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    competitor_offers: Mapped[list["CompetitorOffer"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    website_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    offers: Mapped[list["CompetitorOffer"]] = relationship(
        back_populates="competitor",
        cascade="all, delete-orphan",
    )

class CompetitorOffer(Base):
    __tablename__ = "competitor_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id"))
    url: Mapped[str] = mapped_column(String)
    parser_type: Mapped[str] = mapped_column(String, default="html")
    price_selector: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="competitor_offers")
    competitor: Mapped["Competitor"] = relationship(back_populates="offers")
    price_checks: Mapped[list["PriceCheck"]] = relationship (
        back_populates="offer",
        cascade="all, delete-orphan",
    )

class PriceCheck(Base):
    __tablename__ = "price_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_id: Mapped[int] = mapped_column(Integer, ForeignKey("competitor_offers.id"))
    status: Mapped[str] = mapped_column(String)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    offer: Mapped["CompetitorOffer"] = relationship(back_populates="price_checks")
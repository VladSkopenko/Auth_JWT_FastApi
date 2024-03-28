from sqlalchemy import Column, Integer, String, Date, ForeignKey, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=True)
    phone = Column(String(10), nullable=True)
    birthday = Column(Date, nullable=False)
    description = Column(String(300), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), nullable=True, onupdate=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(123), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())

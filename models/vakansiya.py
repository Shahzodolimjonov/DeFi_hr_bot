from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Vakansiya(Base):
    __tablename__ = "vakansiyalar"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kompaniya = Column(String, nullable=False)
    Lavozim = Column(String, nullable=False)
    maosh = Column(String, nullable=False)
    Ish_turi = Column(String, nullable=True)
    malumot = Column(String, nullable=True)
    manzil = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    maps_url = Column(String, nullable=True)
    masul = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)

    def __repr__(self):
        return f"<Vakansiya(kompaniya={self.kompaniya}, maosh={self.maosh})>"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)

    def __repr__(self):
        return f"<Resume(file_path={self.file_path}, description={self.description})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    vakansiyalar = relationship("Vakansiya", backref="user")
    resume = relationship("Resume", backref="user")



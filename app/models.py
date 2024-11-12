from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import Text, BigInteger, Integer, Float, DateTime, ForeignKey

from database import engine

class Base(DeclarativeBase):
    pass

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(Text, nullable=True)
    alternative_name: Mapped[str] = mapped_column(Text, nullable=True)

    countries: Mapped[str] = mapped_column(Text, nullable=True)
    genres: Mapped[str] = mapped_column(Text, nullable=True)

    fees_ru: Mapped[int] = mapped_column(BigInteger, nullable=True)
    fees_world: Mapped[int] = mapped_column(BigInteger, nullable=True)

    rating_kp: Mapped[float] = mapped_column(Float, nullable=True)
    rating_imdb: Mapped[float] = mapped_column(Float, nullable=True)

    critics_ru: Mapped[float] = mapped_column(Float, nullable=True)
    critics_world: Mapped[float] = mapped_column(Float, nullable=True)

    year: Mapped[int] = mapped_column(Integer, nullable=True)

    premiere_ru: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    premiere_world: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    duration: Mapped[int] = mapped_column(Integer, nullable=True)

    ratingMpaa: Mapped[str] = mapped_column(Text, nullable=True)
    ratingAge: Mapped[int] = mapped_column(Integer, nullable=True)

    networks: Mapped[str] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    persons: Mapped[list["Person"]] = relationship("Person", back_populates="movie")

class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id"),
    )
    movie: Mapped["Movie"] = relationship("Movie", back_populates="persons")

    name: Mapped[str] = mapped_column(Text, nullable=True)
    en_name: Mapped[str] = mapped_column(Text, nullable=True)

    profession: Mapped[str] = mapped_column(Text, nullable=True)
    en_profession: Mapped[str] = mapped_column(Text, nullable=True)

def create_tables():
    Base.metadata.create_all(engine)
    print("Таблицы созданы в базе данных PostgreSQL.")

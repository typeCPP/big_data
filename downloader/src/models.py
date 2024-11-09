from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapped_column
from sqlalchemy import Text, BigInteger, Integer, Double, DateTime
from sqlalchemy import create_engine



DB_URL = 'postgresql://localhost:5432/big_data'
engine = create_engine(DB_URL, echo=True)
session = sessionmaker(engine)()


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(Text, nullable=True)
    alternative_name: Mapped[str] = mapped_column(Text, nullable=True)

    countries: Mapped[str] = mapped_column(Text, nullable=True)

    genres: Mapped[str] = mapped_column(Text, nullable=True)

    fees_ru: Mapped[int] = mapped_column(BigInteger, nullable=True)
    fees_world: Mapped[int] = mapped_column(BigInteger, nullable=True)

    rating_kp: Mapped[int] = mapped_column(Double, nullable=True)
    rating_imdb: Mapped[int] = mapped_column(Double, nullable=True)

    critics_ru: Mapped[int] = mapped_column(Double, nullable=True)
    critics_world: Mapped[int] = mapped_column(Double, nullable=True)

    year: Mapped[int] = mapped_column(Integer, nullable=True)

    premiere_ru: Mapped[str] = mapped_column(DateTime, nullable=True)
    premiere_world: Mapped[str] = mapped_column(DateTime, nullable=True)

    duration: Mapped[int] = mapped_column(Integer, nullable=True)

    ratingMpaa: Mapped[int] = mapped_column(Text, nullable=True)
    ratingAge: Mapped[int] = mapped_column(Integer, nullable=True)

    networks: Mapped[int] = mapped_column(Text, nullable=True)


def create_tables() -> None:
    Base.metadata.create_all(engine)


def add_movie_to_db(movie: Movie):
    session.add(movie)
    session.commit()

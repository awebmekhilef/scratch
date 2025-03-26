from typing import Optional, List
from datetime import datetime, timezone
from hashlib import md5
from slugify import slugify
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship, validates
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    website: Mapped[Optional[str]] = mapped_column(String(100))
    about: Mapped[Optional[str]] = mapped_column(String(5000))

    games: WriteOnlyMapped['Game'] = relationship(back_populates='creator')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'<User \'{self.username}\'>'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


game_tag = Table(
    'game_tag',
    db.metadata,
    Column('game_id', Integer(), ForeignKey('game.id'), primary_key=True),
    Column('tag_id', Integer(), ForeignKey('tag.id'), primary_key=True)
)


class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(50))
    tagline: Mapped[Optional[str]] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(String(5000))
    cover_url: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)

    creator: Mapped[User] = relationship(back_populates='games')
    uploads: WriteOnlyMapped['Upload'] = relationship(back_populates='game')
    screenshots: WriteOnlyMapped['Screenshot'] = relationship(back_populates='game')
    tags: Mapped[List['Tag']] = relationship(secondary=game_tag, back_populates='games')

    @validates('title')
    def validate_title(self, key, title):
        self.slug = slugify(title)
        return title

    def __repr__(self):
        return f'<Game \'{self.title}\'>'


class Upload(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(256))
    filename: Mapped[str] = mapped_column(String(256))
    size: Mapped[int]
    is_web_build: Mapped[bool]
    game_id: Mapped[int] = mapped_column(ForeignKey(Game.id), index=True)

    game: Mapped[Game] = relationship(back_populates='uploads')

    def __repr__(self):
        return f'<Upload \'{self.url}\'>'


class Screenshot(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(256))
    order: Mapped[int]
    game_id: Mapped[int] = mapped_column(ForeignKey(Game.id), index=True)

    game: Mapped[Game] = relationship(back_populates='screenshots')

    def __repr__(self):
        return f'<Screenshot \'{self.url}\'>'


class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    games: WriteOnlyMapped[Game] = relationship(secondary=game_tag, back_populates='tags')

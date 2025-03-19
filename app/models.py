from datetime import datetime, timezone
from hashlib import md5
from typing import Optional
from slugify import slugify
from markdown import markdown
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship, validates
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    website: Mapped[Optional[str]] = mapped_column(String(128))
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


class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(128))
    tagline: Mapped[Optional[str]] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(String(5000))
    cover_filepath: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)

    creator: Mapped[User] = relationship(back_populates='games')
    upload: Mapped['Upload'] = relationship(back_populates='game')
    screenshots: WriteOnlyMapped['Screenshot'] = relationship(back_populates='game')

    @validates('title')
    def _generate_slug(self, key, title):
        self.slug = slugify(title)
        return title

    def markdown(self):
        return markdown(self.description)

    def __repr__(self):
        return f'<Game \'{self.title}\'>'


class Upload(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    filepath: Mapped[str] = mapped_column(String(256))
    size: Mapped[str] = mapped_column(String(16))
    game_id: Mapped[int] = mapped_column(ForeignKey(Game.id), index=True)

    game: Mapped[Game] = relationship(back_populates='upload')


class Screenshot(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    filepath: Mapped[str] = mapped_column(String(256))
    order: Mapped[int] = mapped_column()
    game_id: Mapped[int] = mapped_column(ForeignKey(Game.id), index=True)

    game: Mapped[Game] = relationship(back_populates='screenshots')

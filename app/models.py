from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    about: Mapped[Optional[str]] = mapped_column(String(1000))
    website: Mapped[Optional[str]] = mapped_column(String(256))

    games: WriteOnlyMapped['Game'] = relationship(back_populates='creator')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User \'{self.username}\'>'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)

    creator: Mapped[User] = relationship(back_populates='games')

    def __repr__(self):
        return f'<Game \'{self.title}\'>'

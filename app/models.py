from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from app import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    
    games: WriteOnlyMapped['Game'] = relationship(back_populates='creator')

    def __repr__(self):
        return f'<User \'{self.username}\'>'


class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)

    creator: Mapped[User] = relationship(back_populates='games')

    def __repr__(self):
        return f'<Game \'{self.title}\'>'
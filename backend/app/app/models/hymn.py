from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .office_parts import BlockMixin, LineMixin

hymn_line_association_table = Table(
    "hymn_line_association_table",
    Base.metadata,
    Column("hymn_line_id", Integer, ForeignKey("hymnline.id"), primary_key=True),
    Column("hymn_verse_id", ForeignKey("hymn_verse.id"), primary_key=True),
)


hymn_verse_association_table = Table(
    "hymn_verse_association_table",
    Base.metadata,
    Column("hymn_verse_id", Integer, ForeignKey("hymn_verse.id"), primary_key=True),
    Column("hymn_id", ForeignKey("hymn.id"), primary_key=True),
)


class HymnLine(Base, LineMixin):
    """Lines of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_lines")
    hymn_verses = relationship(
        "Hymn_Verse",
        secondary=hymn_line_association_table,
        back_populates="lines",
        lazy="joined",
    )


class Hymn_Verse(Base, BlockMixin):
    """Hymn_Verses of hymns."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymn_verses")

    lines = relationship(
        "HymnLine",
        secondary=hymn_line_association_table,
        back_populates="hymn_verses",
        lazy="joined",
    )

    hymns = relationship(
        "Hymn",
        secondary=hymn_verse_association_table,
        back_populates="hymn_verses",
        lazy="joined",
    )


class Hymn(Base, BlockMixin):
    """Hymns themselves."""

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="hymns")

    hymns = relationship(
        "Hymn_Verse",
        secondary=hymn_verse_association_table,
        back_populates="hymns",
        lazy="joined",
    )
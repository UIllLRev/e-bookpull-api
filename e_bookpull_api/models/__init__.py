from sqlalchemy import Column, Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import ENUM
from .. import db

class Work(db.Model):
    __tablename__ = 'works'
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}
    id = Column('author_code', Integer, primary_key=True)
    author_name = Column(String(80))
    article_name = Column(Text)
    volume = Column(SmallInteger)
    issue = Column(SmallInteger)
    comments = Column(Text)
    bookpuller = Column(Text)
    duedate = Column(Date)

class Source(db.Model):
    __tablename__ = 'sources'
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}
    id = Column(Integer, primary_key=True)
    author_code = Column(Integer, ForeignKey('works.author_code'), nullable=False)
    type = Column(ENUM('B', 'C', 'J', 'L', 'M', 'P'), index=True)
    citation = Column(Text)
    url = Column(Text)
    comments = Column(Text)
    ordered = Column(Date)
    status_code = Column(ENUM('N', 'E', 'M', 'R', 'X', 'XP', 'XR'), default='N', index=True)
    work = db.relationship('Work', backref=db.backref('sources'))

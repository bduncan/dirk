from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Table,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)


Index('project_name_index', Project.name, unique=True, mysql_length=255)

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

Index('person_name_index', Person.name, unique=True, mysql_length=255)

dependencies = Table("depends", Base.metadata,
    Column("id", Integer),
    Column("parent", Integer, ForeignKey("projects.id")),
    Column("child", Integer, ForeignKey("projects.id")))

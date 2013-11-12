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
    name = Column(Text, nullable=False)
    description = Column(Text)
    owner = Column(Integer, ForeignKey("people.id"))

    def __init__(self, name, description):
        self.name = name
        self.description = description

Index('project_name_index', Project.name, unique=True, mysql_length=255)

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    def __init__(self, name):
        self.name = name

Index('person_name_index', Person.name, unique=True, mysql_length=255)

class Dependency(Base):
    __tablename__ = 'depends'
    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey("projects.id"))
    child = Column(Integer, ForeignKey("projects.id"))

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

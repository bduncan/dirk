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
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


contributors = Table("contributors", Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey("project.id")),
    Column('person_id', Integer, ForeignKey("person.id")),
    )

class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    contributors = relationship("Person", secondary=contributors, backref="projects")

Index('project_name_index', Project.name, unique=True, mysql_length=255)

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

Index('person_name_index', Person.name, unique=True, mysql_length=255)

class Dependency(Base):
    __tablename__ = 'depends'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("project.id"))
    parent = relationship("Project", backref="requires", foreign_keys=[parent_id])
    child_id = Column(Integer, ForeignKey("project.id"))
    child = relationship("Project", backref="enables", foreign_keys=[child_id])

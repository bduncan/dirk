from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Table,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("people.id", ondelete='RESTRICT'))
    owner = relationship("Person", backref="projects", single_parent=True)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    @hybrid_property
    def label(self):
        if self.owner:
            return "%s\\n(%s)" % (self.name, self.owner.name)
        else:
            return self.name

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
    parent_id = Column(Integer, ForeignKey("projects.id"))
    parent = relationship("Project", backref="requires", foreign_keys=[parent_id])
    child_id = Column(Integer, ForeignKey("projects.id"))
    child = relationship("Project", backref="enables", foreign_keys=[child_id])

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import aliased

from .models import (
    DBSession,
    Project,
    Person,
    Dependency,
    )


@view_config(route_name='home', renderer='templates/home.pt')
def my_view(request):
    try:
        projects = DBSession.query(Project).order_by(Project.name).all()
        people = DBSession.query(Person).order_by(Person.name).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'projects': projects,
            'people': people,
            'title': 'dirk',
            'add_person_url': request.route_url('add_person'),
            'add_project_url': request.route_url('add_project'),
            }

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_dirk_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

@view_config(route_name='view_graph')
def graph_view(request):
    try:
        #projects = DBSession.query(Project).all()
        #people = DBSession.query(Person).all()
        #depends = DBSession.query(depends).all()
        import pygraphviz
        graph = pygraphviz.AGraph(directed=True)
        graph.add_nodes_from(x.name for x in DBSession.query(Project.name).all())
        child_alias = aliased(Project)
        graph.add_edges_from(DBSession.query(Project.name, child_alias.name).join(Dependency, Project.id==Dependency.parent).join(child_alias, child_alias.id==Dependency.child).all())
        return Response(graph.draw(format="svg", prog="dot"), content_type='image/svg+xml')
    except DBAPIError:
        conn_err_msg = """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="10cm" height="10cm" viewBox="0 0 1000 300"
     xmlns="http://www.w3.org/2000/svg" version="1.1">
  <desc>Database connection error message</desc>

  <text x="0" y="0"
        font-family="Verdana" font-size="25" fill="red" >
Pyramid is having a problem using your SQL database.  The problem
<tspan x="0" dy="1.2em">
might be caused by one of the following things:
</tspan>
<tspan x="0" dy="2.2em">
1.  You may need to run the "initialize_dirk_db" script
    </tspan>
    <tspan x="0" dy="1.2em">
    to initialize your database tables.  Check your virtual
    </tspan>
    <tspan x="0" dy="1.2em">
    environment's "bin" directory for this script and try to run it.
</tspan>
<tspan x="0" dy="2.2em">
2.  Your database server may not be running.  Check that the
    </tspan>
    <tspan x="0" dy="1.2em">
    database server referred to by the "sqlalchemy.url" setting in
    </tspan>
    <tspan x="0" dy="1.2em">
    your "development.ini" file is running.
</tspan>
<tspan x="0" dy="2.2em">
After you fix the problem, please restart the Pyramid application to
</tspan>
<tspan x="0" dy="1.2em">
try it again.
  </tspan>
  </text>

</svg>
"""
        return Response(conn_err_msg, content_type='image/svg+xml', status_int=500)

@view_config(route_name='add_person')
def add_person_view(request):
    if 'form.submitted' in request.params and 'name' in request.params:
        p = Person(request.params['name'])
        DBSession.add(p)
    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='view_person', renderer='templates/view_person.pt')
def view_person_view(request):
    person = DBSession.query(Person).filter(Person.name==request.matchdict['name']).one()
    projects = DBSession.query(Project).filter(Project.owner==person.id).order_by(Project.name).all()
    return {'person': person,
            'projects': projects,
            'home_url': request.route_url('home'),
            'edit_person_url': request.route_url('edit_person', name=request.matchdict['name']),
            'delete_person_url': request.route_url('delete_person', name=request.matchdict['name']),
           }

@view_config(route_name='delete_person')
def delete_person_view(request):
    if request.method == 'POST':
        person = DBSession.query(Person).filter(Person.name==request.matchdict['name']).one()
        DBSession.delete(person)
    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='add_project')
def add_project_view(request):
    if 'form.submitted' in request.params and 'name' in request.params:
        p = Project(request.params['name'])
        DBSession.add(p)
    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='edit_project', renderer='templates/edit_project.pt')
def edit_project_view(request):
    project = DBSession.query(Project).filter(Project.name==request.matchdict['name']).one()
    if 'form.submitted' in request.params:
        project.description = request.params['description']
        project.owner = request.params['owner'] or None
        return HTTPFound(location=request.route_url('view_project', name=request.matchdict['name']))
    people = DBSession.query(Person).order_by(Person.name).all()
    return {'project': project, 'people': people}

@view_config(route_name='view_project', renderer='templates/view_project.pt')
def view_project_view(request):
    project = DBSession.query(Project, Person).filter(Project.name==request.matchdict['name']).outerjoin(Person, Person.id==Project.owner).one()
    return {'project': project.Project,
            'owner': project.Person,
            'home_url': request.route_url('home'),
            'edit_project_url': request.route_url('edit_project', name=request.matchdict['name']),
            'depends_project_url': request.route_url('project_depends', name=request.matchdict['name']),
            'delete_project_url': request.route_url('delete_project', name=request.matchdict['name']),
           }

@view_config(route_name='delete_project')
def delete_project_view(request):
    if request.method == 'POST':
        project = DBSession.query(Project).filter(Project.name==request.matchdict['name']).one()
        DBSession.delete(project)
    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='project_depends', renderer='templates/depends_project.pt')
def depends_project_view(request):
    project = DBSession.query(Project).filter(Project.name==request.matchdict['name']).one()
    if 'form.submitted' in request.params and request.method == 'POST':
        # Insert all the projects listed in "requires"
        requires = request.params.getall('requires')
        print "requires",requires
        for require in requires:
            d = Dependency(parent=DBSession.query(Project).filter(Project.name==require).one().id, child=project.id)
            DBSession.add(d)
        if not requires:
            # Nothing requires this project
            DBSession.query(Dependency).filter(Dependency.child==project.id).delete()
        else:
            # Delete all the projects not listed in "requires"
            DBSession.query(Dependency).filter(Dependency.parent==project.id).filter(Dependency.child.in_(DBSession.query(Project.id).filter(~Project.name.in_(requires)))).delete(synchronize_session='fetch')

        enables = request.params.getall('enables')
        print "enables",enables
        # Insert all the projects listed in "enables"
        for enable in enables:
            print "enabling",enable
            d = Dependency(parent=project.id, child=DBSession.query(Project).filter(Project.name==enable).one().id)
            DBSession.add(d)
        if not enables:
            # Nothing enables this project
            DBSession.query(Dependency).filter(Dependency.parent==project.id).delete()
        else:
            # Delete all the projects not listed in "enables"
            DBSession.query(Dependency).filter(Dependency.child==project.id).filter(Dependency.parent.in_(DBSession.query(Project.id).filter(~Project.name.in_(enables)))).delete(synchronize_session='fetch')
        return HTTPFound(location=request.route_url('view_project', name=request.matchdict['name']))
    requires = DBSession.query(Project).join(Dependency, Dependency.parent==Project.id).filter(Dependency.child==project.id).order_by(Project.name).all()
    enables = DBSession.query(Project).join(Dependency, Dependency.child==Project.id).filter(Dependency.parent==project.id).order_by(Project.name).all()
    projects = DBSession.query(Project).order_by(Project.name).all()
    return {'project': project,
            'requires': requires,
            'enables': enables,
            'projects': projects,
           }

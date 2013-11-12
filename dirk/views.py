from pyramid.response import Response
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
        projects = DBSession.query(Project).all()
        people = DBSession.query(Person).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'projects': projects, 'people': people, 'title': 'dirk'}

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
        graph.add_edges_from(DBSession.query(Dependency).join(Project, Project.id==Dependency.parent).join(child_alias, Project.id==Dependency.child).all())
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

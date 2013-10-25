from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('view_person', '/person/{name}')
    config.add_route('view_project', '/project/{name}')
    config.add_route('add_person', '/person/add/{name}')
    config.add_route('add_project', '/project/add/{name}')
    config.add_route('edit_person', '/person/{name}/edit')
    config.add_route('edit_project', '/project/{name}/edit')
    config.scan()
    return config.make_wsgi_app()

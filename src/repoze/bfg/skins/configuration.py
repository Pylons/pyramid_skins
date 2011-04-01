from repoze.bfg.skins.zcml import skins
from repoze.bfg.path import caller_path
from zope.configuration.config import ConfigurationMachine


def register_path(path, discovery=False, indexes=[], request_type=None):
    path = caller_path(path)
    context = ConfigurationMachine()
    stmt = skins(context, path, discovery, request_type)
    for index in indexes:
        stmt.view(context, index)
    stmt.configure()


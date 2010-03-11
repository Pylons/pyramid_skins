from repoze.bfg.skins.zcml import skins
from repoze.bfg.path import caller_path
from zope.configuration.config import ConfigurationMachine


def register_path(path, discovery=False, indexes=[]):
    path = caller_path(path)
    context = ConfigurationMachine()
    stmt = skins(context, path, discovery)
    for index in indexes:
        stmt.view(context, index)
    stmt.configure()


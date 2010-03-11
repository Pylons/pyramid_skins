from repoze.bfg.skins.zcml import skins
from zope.configuration.config import ConfigurationMachine


def register_path(path, discovery=False, indexes=[]):
    context = ConfigurationMachine()
    stmt = skins(context, path, discovery)
    for index in indexes:
        stmt.view(context, index)
    stmt.configure()


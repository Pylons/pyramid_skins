from pyramid.traversal import ModelGraphTraverser

class RoutesTraverserFactory(ModelGraphTraverser):
    def __call__(self, environ):
        tdict = super(RoutesTraverserFactory, self).__call__(environ)
        tdict['view_name'] = '_'.join(tdict['subpath'])
        return tdict

def RoutesTraverser(factory):
    return factory

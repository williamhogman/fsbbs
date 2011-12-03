from jinja2 import Environment,FileSystemLoader
import ext

class TemplateEngine(object):
    """
    Class wrapping the jinja2 template system with our filters
    """

    def __init__(self,path):
        """ 
        Constructs a new instance of TemplatEngine operating in the
        passed in folder.
        """
        self.env = Environment(loader=FileSystemLoader(path))
        for f in ext.filters:
            self.env.filters[f.__name__] = f
        
    def _get_template(self,name):
        return self.env.get_template(name)

    def render(self,name,data):
        """ 
        returns an object with a dump function that can be called on a
        file-like object
        """
        return self._get_template(name).stream(data)

    def dump(self,name,data,fp):
        """ writes a rendered template to a file for output """
        self.render(name,data).dump(fp)




    

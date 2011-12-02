from zope.interface import Interface,Attribute

class IAuthModule(Interface):
    """ Interface that authmodule have to implement"""
    module_type = Attribute("""returns the type of the module. one of the PAM module types""")

    def call(chain):
        """ call this auth module """

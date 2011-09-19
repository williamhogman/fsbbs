from zope.interface import Interface,Attribute,implements

class IAuthModule(Interface):
    module_type = Attribute("""returns the type of the module. one of the PAM module types""")

    def call(chain):
        """ call this auth module """

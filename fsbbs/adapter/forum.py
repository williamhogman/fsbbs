from fsbbs.adapter.base import View,AttrField,ViewContents


class Frontpage(View):
    name = AttrField("name")
    tagline = AttrField("tagline")
    contents = ViewContents()

class Forum(View):
    name = AttrField("name")
    tagline = AttrField("tagline")
                     
    
class Category(View):
    name = AttrField("name")
    description = AttrField("description")

class CategoryPage(View):
    name = AttrField("name")
    description = AttrField("description")
    contents = ViewContents()


                     

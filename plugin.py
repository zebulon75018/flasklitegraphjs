import importlib
import os

class pluginManager:
    def __init__(self, path):
        self._path = path
        self._modules = {}
        self._loadmodules()

    def _loadmodules(self):
        for filepy in os.listdir(self._path):
            if filepy == "__init__.py":
                continue

            if filepy[-2:] == "py":
                modulename = os.path.join(self._path,filepy[:-3]).replace(os.sep,".")
                self._modules[filepy[:-3]] = importlib.import_module(modulename)

    def reloadModules(self):
        for key in self._modules:
            reload(self._modules[key])

    @property
    def modules(self):
        return self._modules

    def classes(self):
        for key in self._modules:
            for c in dir(self._modules[key]):
                 if not c.startswith("__"):
                        my_class = getattr(self._modules[key], c)
                        yield my_class()


if __name__ == "__main__":
	from jinja2 import Environment, PackageLoader, select_autoescape
	env = Environment( loader=PackageLoader("plugin", package_path='templates'), autoescape=select_autoescape())
	template = env.get_template("plugins.js")
	data =[] 
	pm = pluginManager("plugins")
	for obj in pm.classes():
    		typenode = {}
    		for member in obj.__dict__:
        		strsplitted = member.split("_")
        		if strsplitted[0] not in typenode:
              			typenode[strsplitted[0]] = []
        		typenode[strsplitted[0]].append({'type':strsplitted[1],'name':strsplitted[2], 'value':obj.__dict__[member]})
    		data.append({"name": type(obj).__name__, "type":typenode})
                
	print(template.render(data=data))

"""
pm.reloadModules()
for obj in pm.classes():
    print(obj)
"""


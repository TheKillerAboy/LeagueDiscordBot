import os
import importlib.util

def import_module(python_file_abs):
    spec = importlib.util.spec_from_file_location(python_file_abs[python_file_abs.rindex(os.path.sep) + 1:python_file_abs.rindex('.py')],
                                                  python_file_abs)
    imp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(imp)
    return imp
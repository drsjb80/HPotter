# https://stackoverflow.com/questions/5048329/python-decorator-for-automatic-binding-init-arguments

from functools import wraps

def lazy_init(init):
    import inspect
    arg_names = inspect.getargspec(init)[0]

    @wraps(init)
    def new_init(self, *args):
        for name, value in zip(arg_names[1:], args):
            setattr(self, name, value)
        init(self, *args)

    return new_init

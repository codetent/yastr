import inspect
from contextlib import ExitStack, contextmanager
from weakref import finalize

from wrapt import ObjectProxy


class FixtureLookupError(LookupError):

    def __init__(self, argname: str) -> None:
        super().__init__(argname)
        self.argname = argname

    def __str__(self) -> str:
        return f'fixture \'{self.argname}\' not found'


class FixtureRequest:

    def __init__(self, node) -> None:
        self.node = node
        self.session = node.session
        self.fixturename = None
        self.scope = 'session'
        self.config = node.config
        self.function = None
        self.cls = None
        self.instance = None
        self.module = None
        self.fspath = node.fspath
        self.keywords = node.keywords

        self._fixture_manager = node.session._fixturemanager
        self._fixture_info = self._fixture_manager.getfixtureinfo(node, None, None, funcargs=False)
        self._fixture_defs = self._fixture_manager.getfixtureclosure(self._fixture_info.names_closure, node)[2]

        self._cache = {}
        self._stack = ExitStack()

        finalize(self, self._stack.close)

    def __repr__(self) -> str:
        return f'<FixtureRequest for {self.node!r}>'

    @property
    def fixturenames(self):
        return list(self._fixture_defs.keys())

    def addfinalizer(self, finalizer):
        self._stack.callback(finalizer)

    def applymarker(self, marker):
        self.node.add_marker(marker)

    def raiseerror(self, msg):
        raise FixtureLookupError(msg)

    def getfixturevalue(self, name):
        if name == 'request':
            return self

        if name in self._cache:
            return self._cache[name]

        try:
            fixture_def = self._fixture_defs[name][0]
        except (KeyError, IndexError):
            self.raiseerror(name)

        func = fixture_def.func
        sig = inspect.signature(func)
        param_names = sig.parameters.keys()
        param_values = {param: SubRequest(self, name).getfixturevalue(param) for param in param_names}

        if inspect.isgeneratorfunction(func):
            func = contextmanager(func)
            cm = func(**param_values)
            value = self._stack.enter_context(cm)
        else:
            value = func(**param_values)

        self._cache[name] = value
        return value

    def _execute(self):
        fixture_names = tuple(arg for mark in self.node.iter_markers(name='usefixtures') for arg in mark.args)
        for name in fixture_names:
            self.getfixturevalue(name)

    def _teardown(self):
        self._stack.close()


class SubRequest(ObjectProxy):

    def __init__(self, request: FixtureRequest, fixturename: str):
        super().__init__(request)
        self._self_fixturename = fixturename

    def __repr__(self) -> str:
        return f'<SubRequest {self.fixturename!r} for {self.node!r}>'

    @property
    def fixturename(self):
        return self._self_fixturename

    def getfixturevalue(self, name):
        if name == 'request':
            return self

        return self.__wrapped__.getfixturevalue(name)

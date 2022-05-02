import inspect
from contextlib import ExitStack, contextmanager
from weakref import finalize

from wrapt import ObjectProxy


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
        return self._fixture_defs.keys()

    def addfinalizer(self, finalizer):
        self._stack.callback(finalizer)

    def applymarker(self, marker):
        self.node.add_marker(marker)

    def raiseerror(self, msg):
        raise self._fixture_manager.FixtureLookupError(None, self, msg)

    def getfixturevalue(self, name):
        if name == 'request':
            return self

        if name in self._cache:
            return self._cache[name]

        request = SubRequest(self, name)
        value = request._execute()

        self._cache[name] = value
        return value

    def _execute(self):
        fixture_names = tuple(arg for mark in self.node.iter_markers(name='usefixtures') for arg in mark.args)
        for name in fixture_names:
            self.getfixturevalue(name)

    def _teardown(self):
        self._stack.close()


class SubRequest(ObjectProxy):

    def __init__(self, request: FixtureRequest, name: str):
        super().__init__(request)
        self.fixturename = name

    def __repr__(self) -> str:
        return f'<SubRequest {self.fixturename!r} for {self.node!r}>'

    def getfixturevalue(self, name):
        if name == 'request':
            return self

        return self.__wrapped__.getfixturevalue(name)

    def _execute(self):
        fixture_def = self._fixture_defs[self.fixturename][0]
        func = fixture_def.func
        sig = inspect.signature(func)
        param_names = sig.parameters.keys()
        param_values = {name: self.getfixturevalue(name) for name in param_names}

        if inspect.isgeneratorfunction(func):
            func = contextmanager(func)
            cm = func(**param_values)
            return self._stack.enter_context(cm)
        else:
            return func(**param_values)

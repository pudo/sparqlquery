class TelescopeError(Exception):
    pass

class CompileError(TelescopeError):
    pass

class NotSupportedError(TelescopeError):
    pass

class InvalidRequestError(TelescopeError):
    pass

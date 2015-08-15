class SparqlQueryError(Exception):
    pass


class CompileError(SparqlQueryError):
    pass


class NotSupportedError(SparqlQueryError):
    pass


class InvalidRequestError(SparqlQueryError):
    pass

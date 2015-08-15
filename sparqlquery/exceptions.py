class sparqlqueryError(Exception):
    pass


class CompileError(sparqlqueryError):
    pass


class NotSupportedError(sparqlqueryError):
    pass


class InvalidRequestError(sparqlqueryError):
    pass

class ResolveException(Exception):
    pass


class EnumeratedValueContainerException(ResolveException):
    pass


class LoopException(ResolveException):
    pass


class ResolverGraphException(Exception):
    pass

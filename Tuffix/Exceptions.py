##########################################################################
# exception types
# AUTHORS: Kevin Wortman , Jared Dyreson
##########################################################################

class MessageException(Exception):
    """
    Base types for exceptions that include a string message
    """

    def __init__(self, message):
        if not (isinstance(message, str)):
            raise ValueError
        self.message = message


class UsageError(MessageException):
    """
    Commandline usage error
    """

    def __init__(self, message):
        super().__init__(message)


class EnvironmentError(MessageException):
    """
    Problem with the environment (wrong OS, essential shell command missing, etc.)
    """

    def __init__(self, message):
        super().__init__(message)


class StatusError(MessageException):
    """
    Issue reported by the `status` command, that's at the level of a fatal error
    """

    def __init__(self, message):
        super().__init__(message)


class StatusWarning(MessageException):
    """
    Issue reported by the `status` command, that's at the level of a nonfatal warning
    """

    def __init__(self, message):
        super().__init__(message)


class UnknownUserException(MessageException):
    """
    issue reported when sudo_run class cannot find a given user.
    Use for internal API
    """

    def __init__(self, message):
        super().__init__(message)


class PrivilageExecutionException(MessageException):
    """
    issue reported when root code execution is invoked by non privilaged user.
    Use for internal API
    """

    def __init__(self, message):
        super().__init__(message)

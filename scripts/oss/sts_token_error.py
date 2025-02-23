class StsTokenError(Exception):

    def __init__(self, status):
        """Initialize."""
        super(StsTokenError, self).__init__(status)
        self.status = status

class GnuplotError(Exception):

    def __init__(self, message):
        self.args = (message,)
        self.message = message

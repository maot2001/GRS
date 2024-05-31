class Belong:
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.items = kwargs.values()
        self.args = args
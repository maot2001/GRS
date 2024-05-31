class Interaction:
    def __init__(self, user, comment=None, value=None, *args, **kwargs):
        self.user = user
        self.items = kwargs.values()
        self.args = args
        
        if comment:
            self.comment = comment
        if value:
            self.value = value

    def add_comment(self, comment):
        if self.comment:
            if isinstance(self.comment, list):
                self.comment.append(comment)
            else:
                self.comment = [self.comment, comment]
        else:
            self.comment = comment

    def add_value(self, value):
        if self.value:
            if isinstance(self.value, list):
                self.value.append(value)
            else:
                self.value = [self.value, value]
        else:
            self.value = value
        
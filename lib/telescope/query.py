class Query(object):
    def __init__(self, class_, session=None):
        self.class_ = class_
        self.session = session

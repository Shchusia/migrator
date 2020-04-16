
class DbUtil(object):
    def _connect(self):
        raise NotImplementedError

    def _disconnect(self):
        raise NotImplementedError

    def __del__(self):
        self._disconnect()


class Observable:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, args):
        for obs in self._observers:
            obs.notify(self, args)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

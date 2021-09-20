class Observer:

    def __init__(self, observable):
        observable.subscribe(self)

    def notify(self,observable,args):
        print ('Got', args, 'From', observable)
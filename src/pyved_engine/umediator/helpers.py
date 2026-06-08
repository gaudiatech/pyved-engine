class EventReadyCls:
    def __init__(self, mediator):
        super().__init__()
        if mediator is None:
            raise ValueError("a mediator instance is required")
        self._mediator = mediator

    def pev(self, event_type, event=None, delivery=None):
        if delivery is None:
            from .protocol import Delivery
            delivery = Delivery.LOCAL
        self._mediator.post(event_type, event, delivery=delivery)

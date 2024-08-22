class EventDispatcher:
    def __init__(self):
        self._handlers = {}

    def add_event_listener(self, event_name, handler):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def remove_event_listener(self, event_name, handler):
        if event_name in self._handlers:
            self._handlers[event_name].remove(handler)
            if not self._handlers[event_name]:
                del self._handlers[event_name]

    def dispatch_event(self, event_name, *args, **kwargs):
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                handler(*args, **kwargs)

# 사용 예시
def on_custom_event(data):
    print(f"Custom event triggered with data: {data}")

dispatcher = EventDispatcher()

dispatcher.add_event_listener("custom_event", on_custom_event)

# 이벤트 디스패치
dispatcher.dispatch_event("custom_event", {"key": "value"})

# 핸들러 제거
dispatcher.remove_event_listener("custom_event", on_custom_event)
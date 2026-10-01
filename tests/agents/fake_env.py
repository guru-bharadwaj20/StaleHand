"""A browser-free stand-in for BrowserEnv: screenshots are b"screen-<step>", and actions are only recorded."""
from stalehand.env.actions import Click
from stalehand.env.browser import Observation


class FakeEnv:
    def __init__(self, commit_on_click=None, external_at=()):
        self.step, self.actions, self.began = 0, [], 0
        self.commit_on_click = commit_on_click  # item id to log as committed on the first click
        self.external_at = set(external_at)     # steps at which a scheduled change "lands"
        self._external, self._events = 0, []

    def reset(self, scenario):
        self.scenario, self.step, self.actions, self._events = scenario, 0, [], []
        return self.observe()

    def observe(self):
        return Observation(self.step, f"screen-{self.step}".encode())

    def begin_action(self):
        self.began += 1

    def act(self, action):
        self.actions.append(action)
        if isinstance(action, Click) and self.commit_on_click and not self._events:
            self._events.append({"kind": "send", "itemId": self.commit_on_click, "commit": True})
        self.step += 1
        if self.step in self.external_at:
            self._external += 1
        return self.observe()

    def events(self):
        return list(self._events)

    def mark_external(self):
        self._external = 0

    def external_since_mark(self):
        return self._external

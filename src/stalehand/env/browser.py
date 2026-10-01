"""Playwright environment around a StaleHand web app.

Step semantics: reset() loads the scenario and returns the step-0 screen (what the planner sees). Each act()
advances the step by one. Changes scheduled for step k land at one of two moments:
  before_observation  before the step-k screenshot, so the executor sees them (stale subtask setting)
  mid_step            after the step-k screenshot, just before the action (time-of-check/time-of-use setting);
                      begin_action() applies them, and act() calls it if the agent did not
  after_handoff       after the planner has written a subtask at step k, before the executor's next screenshot:
                      the executor sees the change and the subtask does not (stale handoff setting). handoff()
                      applies them; begin_action() does if no subtask was handed over at that step
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ..scenarios.scenario import Scenario
from ..scenarios.serialize import change_to_dict, scenario_to_dict
from .actions import Click, Done, Key, Scroll, Type, Wait
from .apps import app_url

VIEWPORT = (1288, 728)  # multiples of 28, so Qwen2.5-VL style encoders see the screen unresized

Box = Tuple[float, float, float, float]

_MUTATIONS_JS = """() => {
  window.__stalehandMutations = 0;
  new MutationObserver((records) => { window.__stalehandMutations += records.length; })
    .observe(document.body, {subtree: true, childList: true, attributes: true, characterData: true});
}"""

_BOXES_JS = """() => {
  const out = {};
  for (const el of document.querySelectorAll('[data-item-id][data-role]')) {
    const r = el.getBoundingClientRect();
    const clip = el.closest('.list') ? el.closest('.list').getBoundingClientRect()
                                     : {top: 0, bottom: innerHeight, left: 0, right: innerWidth};
    const top = Math.max(r.top, clip.top), bottom = Math.min(r.bottom, clip.bottom, innerHeight);
    const left = Math.max(r.left, clip.left), right = Math.min(r.right, clip.right, innerWidth);
    if (bottom > top && right > left) out[el.dataset.itemId] = [left, top, right - left, bottom - top];
  }
  return out;
}"""

# Figure annotations for render(): a box around each item, with its label above it, so identity is in the text
_OUTLINE_JS = """(marks) => {
  const colors = ['#b42318', '#1d4ed8'];
  marks.forEach(({box: [x, y, w, h], label}, i) => {
    const c = colors[i % colors.length];
    const frame = document.createElement('div');
    frame.style.cssText = `position:fixed;left:${x - 3}px;top:${y - 3}px;width:${w}px;height:${h}px;` +
      `border:3px ${i % 2 ? 'dashed' : 'solid'} ${c};border-radius:6px;z-index:9999;pointer-events:none`;
    const tag = document.createElement('div');
    tag.textContent = label;
    tag.style.cssText = `position:fixed;left:${x}px;top:${Math.max(0, y - 24)}px;background:${c};color:#fff;` +
      `font:600 13px sans-serif;padding:3px 8px;border-radius:4px;z-index:10000`;
    document.body.append(frame, tag);
  });
}"""

_driver = {"pw": None, "users": 0}  # Playwright allows one sync driver per process; environments share it


def _acquire():
    if _driver["pw"] is None:
        from playwright.sync_api import sync_playwright
        _driver["pw"] = sync_playwright().start()
    _driver["users"] += 1
    return _driver["pw"]


def _release():
    _driver["users"] -= 1
    if _driver["users"] == 0:
        _driver["pw"].stop()
        _driver["pw"] = None


@dataclass(frozen=True)
class Observation:
    step: int
    png: bytes


class BrowserEnv:
    TIMINGS = ("before_observation", "mid_step", "after_handoff")

    def __init__(self, headless: bool = True, channel: Optional[str] = "chrome", change_timing: str = "before_observation"):
        if change_timing not in self.TIMINGS:
            raise ValueError(f"change_timing must be one of {self.TIMINGS}")
        self.change_timing = change_timing
        self._browser = _acquire().chromium.launch(headless=headless, channel=channel)
        self._page = None
        self.scenario: Optional[Scenario] = None
        self.step = 0

    def reset(self, scenario: Scenario) -> Observation:
        if self._page is not None:
            self._page.close()
        self._page = self._browser.new_page(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]})
        self._page.goto(app_url(scenario.domain))
        self._page.evaluate("s => window.stalehand.load(s)", scenario_to_dict(scenario))
        self._page.evaluate(_MUTATIONS_JS)
        self.scenario, self.step, self._external, self._begun, self._landed = scenario, 0, 0, False, -1
        self._event_steps = []
        if self.change_timing == "before_observation":
            self._apply_due_changes()
        return self.observe()

    def begin_action(self) -> None:
        """Mark the moment between the executor's screenshot and its action (mid_step changes land here)."""
        if self.change_timing in ("mid_step", "after_handoff") and not self._begun:
            self._apply_due_changes()
        self._begun = True

    def handoff(self) -> bool:
        """The planner has just handed over a subtask. Under after_handoff, this step's changes land now; returns
        whether the page changed, so the agent knows to take a fresh screenshot for the executor."""
        if self.change_timing != "after_handoff" or self._landed == self.step:
            return False
        return self._apply_due_changes()

    def _apply_due_changes(self) -> bool:
        if self._landed == self.step:
            return False
        self._landed = self.step
        due = [sc for sc in self.scenario.changes if sc.step == self.step]
        if not due:
            return False
        before = self.mutations_since_mark()
        for sc in due:
            self._page.evaluate("c => window.stalehand.apply(c)", change_to_dict(sc.change))
        self._external += self.mutations_since_mark() - before
        return True

    def observe(self) -> Observation:
        return Observation(self.step, self._page.screenshot(type="png"))

    def act(self, action) -> Observation:
        self.begin_action()
        page = self._page
        if isinstance(action, Click):
            page.mouse.click(action.x, action.y)
        elif isinstance(action, Type):
            page.keyboard.type(action.text)
        elif isinstance(action, Key):
            page.keyboard.press(action.key)
        elif isinstance(action, Scroll):
            page.mouse.wheel(action.dx, action.dy)
        elif not isinstance(action, (Done, Wait)):
            raise TypeError(f"unsupported action {action!r}")
        self._tag_events()
        self.step += 1
        self._begun = False
        if self.change_timing == "before_observation":
            self._apply_due_changes()
        return self.observe()

    def mark_mutations(self) -> None:
        """Start counting DOM mutations from now (used by guards that block on any page change)."""
        self._page.evaluate("window.__stalehandMutations = 0")

    def mutations_since_mark(self) -> int:
        return self._page.evaluate("window.__stalehandMutations")

    def mark_external(self) -> None:
        """Start counting DOM mutations caused by scheduled changes only, not by the agent's own actions."""
        self._external = 0

    def external_since_mark(self) -> int:
        return self._external

    def item_boxes(self) -> Dict[str, Box]:
        """Visible part of every item element, in screen pixels: {item_id: (x, y, w, h)}."""
        return {k: tuple(v) for k, v in self._page.evaluate(_BOXES_JS).items()}

    def role_box(self, role: str) -> Optional[Box]:
        box = self._page.locator(f'[data-role="{role}"]').first.bounding_box()
        return None if box is None else (box["x"], box["y"], box["width"], box["height"])

    def _tag_events(self) -> None:
        n = len(self._page.evaluate("window.stalehand.events()"))
        self._event_steps += [self.step] * (n - len(self._event_steps))

    def events(self):
        """App events, each with the env step whose action caused it (None for scheduled page changes)."""
        out = self._page.evaluate("window.stalehand.events()")
        for i, e in enumerate(out):
            e["step"] = self._event_steps[i] if i < len(self._event_steps) and e.get("kind") != "page_change" else None
        return out

    def commits(self):
        return [e for e in self.events() if e.get("commit")]

    def view(self):
        return self._page.evaluate("window.stalehand.view()")

    def render(self, scenario: Scenario, through_step: Optional[int] = None,
               outline: Optional[Dict[str, str]] = None) -> bytes:
        """Screenshot of a scenario without running an episode: its first screen, or the screen once every change up
        to through_step has landed. outline maps item ids to labels drawn around them. Uses its own page, so a live
        episode in this environment is left as it was."""
        page = self._browser.new_page(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]})
        try:
            page.goto(app_url(scenario.domain))
            page.evaluate("s => window.stalehand.load(s)", scenario_to_dict(scenario))
            for sc in scenario.changes:
                if through_step is not None and sc.step <= through_step:
                    page.evaluate("c => window.stalehand.apply(c)", change_to_dict(sc.change))
            if outline:
                boxes = page.evaluate(_BOXES_JS)
                page.evaluate(_OUTLINE_JS, [{"box": boxes[i], "label": label} for i, label in outline.items()
                                            if i in boxes])
            return page.screenshot(type="png")
        finally:
            page.close()

    def close(self) -> None:
        if self._page is not None:
            self._page.close()
        self._browser.close()
        _release()

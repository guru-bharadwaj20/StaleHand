"""Playwright environment around a StaleHand web app.

Step semantics: reset() loads the scenario and returns the step-0 screen (what the planner sees). Each act()
advances the step by one; changes scheduled for the new step are applied before the screenshot is taken, so the
executor's observation at step k already includes them.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ..scenarios.scenario import Scenario
from ..scenarios.serialize import change_to_dict, scenario_to_dict
from .actions import Click, Done, Key, Scroll, Type
from .apps import app_url

VIEWPORT = (1288, 728)  # multiples of 28, so Qwen2.5-VL style encoders see the screen unresized

Box = Tuple[float, float, float, float]

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


@dataclass(frozen=True)
class Observation:
    step: int
    png: bytes


class BrowserEnv:
    def __init__(self, headless: bool = True, channel: Optional[str] = "chrome"):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=headless, channel=channel)
        self._page = None
        self.scenario: Optional[Scenario] = None
        self.step = 0

    def reset(self, scenario: Scenario) -> Observation:
        if self._page is not None:
            self._page.close()
        self._page = self._browser.new_page(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]})
        self._page.goto(app_url(scenario.domain))
        self._page.evaluate("s => window.stalehand.load(s)", scenario_to_dict(scenario))
        self.scenario, self.step = scenario, 0
        self._apply_due_changes()
        return self.observe()

    def _apply_due_changes(self) -> None:
        for sc in self.scenario.changes:
            if sc.step == self.step:
                self._page.evaluate("c => window.stalehand.apply(c)", change_to_dict(sc.change))

    def observe(self) -> Observation:
        return Observation(self.step, self._page.screenshot(type="png"))

    def act(self, action) -> Observation:
        page = self._page
        if isinstance(action, Click):
            page.mouse.click(action.x, action.y)
        elif isinstance(action, Type):
            page.keyboard.type(action.text)
        elif isinstance(action, Key):
            page.keyboard.press(action.key)
        elif isinstance(action, Scroll):
            page.mouse.wheel(action.dx, action.dy)
        elif not isinstance(action, Done):
            raise TypeError(f"unsupported action {action!r}")
        self.step += 1
        self._apply_due_changes()
        return self.observe()

    def item_boxes(self) -> Dict[str, Box]:
        """Visible part of every item element, in screen pixels: {item_id: (x, y, w, h)}."""
        return {k: tuple(v) for k, v in self._page.evaluate(_BOXES_JS).items()}

    def role_box(self, role: str) -> Optional[Box]:
        box = self._page.locator(f'[data-role="{role}"]').first.bounding_box()
        return None if box is None else (box["x"], box["y"], box["width"], box["height"])

    def events(self):
        return self._page.evaluate("window.stalehand.events()")

    def commits(self):
        return [e for e in self.events() if e.get("commit")]

    def view(self):
        return self._page.evaluate("window.stalehand.view()")

    def close(self) -> None:
        if self._page is not None:
            self._page.close()
        self._browser.close()
        self._pw.stop()

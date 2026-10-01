import { test } from "node:test";
import assert from "node:assert/strict";
import { formatTime, initials, rupees } from "../src/core/format.js";

test("minutes after midnight become a 12-hour clock", () => {
  assert.equal(formatTime(0), "12:00 AM");
  assert.equal(formatTime(11 * 60 + 42), "11:42 AM");
  assert.equal(formatTime(12 * 60 + 38), "12:38 PM");
  assert.equal(formatTime(23 * 60 + 5), "11:05 PM");
});

test("initials use the first two words", () => {
  assert.equal(initials("Samuel Lee"), "SL");
  assert.equal(initials("Liam O'Brien Jr"), "LO");
});

test("rupees use Indian digit grouping", () => {
  assert.equal(rupees(1474), "₹1,474");
  assert.equal(rupees(123456), "₹1,23,456");
});

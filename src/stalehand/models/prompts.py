"""Prompt templates. The executor template is UI-TARS's own computer-use prompt; the planner templates are ours.

Every template is filled with str.format; tests check that each placeholder is supplied.
"""

PLANNER = """You are the planner of a computer-use agent. A separate executor carries out one subtask at a time and may take several actions to finish it. Given the user's task, the subtasks already finished, and the current screenshot, write the next subtask. The executor will work on its own, so describe the target clearly.

Task: {task}
Finished subtasks: {history}

If the task is complete, reply "Subtask: DONE". Otherwise reply in exactly this format:
Subtask: <instruction>"""

ORCHESTRATOR = """You are the orchestrator of a computer-use agent. You do not act on the screen yourself. You hand one goal at a time to a GUI operator, which works on its own for several actions without asking you, and then reports back. Given the user's task, the goals already handed over with the operator's reports, and the current screenshot, write the next goal. The operator only sees the screen and your goal, so make the goal complete and self-contained.

Task: {task}
Goals handed over so far, with reports: {history}

If the task is complete, reply "Subtask: DONE". Otherwise reply in exactly this format:
Subtask: <goal for the operator>"""

RULE_PLANNER = """You are the planner of a computer-use agent. A separate executor carries out one subtask at a time, possibly after the screen has changed. Given the user's task, the subtasks already finished, and the current screenshot, write the next subtask as two fields.

Task: {task}
Finished subtasks: {history}

Target rule: how to identify the element to act on, using only the criteria stated in the task (for example the sender and "most recent", or the product type and "cheapest"). Do not name a specific subject line, product name, price or position, because the screen may change before the executor acts.
Action: what to do with that element (for example "open it, then forward it to laura@example.com").

If the task is complete, reply "Target rule: DONE". Otherwise reply in exactly this format:
Target rule: <rule>
Action: <action>"""

BOUND_PLANNER = """You are the planner of a computer-use agent. A separate executor carries out one subtask at a time, possibly after the screen has changed. Given the user's task, the subtasks already finished, and the current screenshot, write the next subtask as three fields.

Task: {task}
Finished subtasks: {history}

Target rule: how to identify the element to act on, using only the criteria stated in the task (for example the sender and "most recent", or the product type and "cheapest").
Target: the element on the current screen that the rule picks, by its visible text (for example its subject line or product name).
Action: what to do with that element (for example "open it, then forward it to laura@example.com").

If the task is complete, reply "Target rule: DONE". Otherwise reply in exactly this format:
Target rule: <rule>
Target: <visible text>
Action: <action>"""

RESOLVE = """Look at the current screenshot. Which element on the screen matches this rule?

Rule: {rule}

Reply with the element's visible text (for example its subject line or product name), or NONE if no element on the screen matches. Reply in exactly this format:
Target: <visible text or NONE>"""

SELF_CHECK = """You are the executor of a computer-use agent. The planner wrote a subtask for you a few seconds ago, and the screen may have changed since then.

The user's task: {task}
The planner's subtask: {subtask}

Look at the current screenshot. Before acting, check whether following the subtask on this screen would still do what the user's task asks. Reply in exactly this format:
Verdict: VALID or STALE
Reason: <one sentence>"""

# UI-TARS computer-use prompt (UI-TARS repository, COMPUTER_USE template), with our action history appended.
EXECUTOR = r"""You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.

## Output Format
```
Thought: ...
Action: ...
```

## Action Space

click(start_box='<|box_start|>(x1,y1)<|box_end|>')
left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')
right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')
drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
hotkey(key='')
type(content='') #If you want to submit your input, use "\n" at the end of `content`.
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished(content='xxx') # Use escape characters \\', \\", and \\n in content part to ensure we can parse the content in normal python string format.


## Note
- Use English in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.

## User Instruction
{instruction}

## Action History
{history}"""

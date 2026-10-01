// Holds an app's state, runs its reducer, applies live changes and keeps the action log.
import { ActionLog, type ActionEvent } from "./log.js";
import type { Change } from "./types.js";

export type Reducer<S, A> = (state: S, action: A) => { state: S; events: ActionEvent[] };
export type Changer<S> = (state: S, change: Change) => S;
export type Listener<S> = (state: S, cause: string) => void;

export class Store<S, A extends { type: string }> {
  readonly log: ActionLog;
  private listeners: Listener<S>[] = [];

  constructor(public state: S, private readonly reducer: Reducer<S, A>, private readonly changer: Changer<S>,
              clock?: () => number) {
    this.log = new ActionLog(clock);
  }

  subscribe(fn: Listener<S>): void {
    this.listeners.push(fn);
  }

  dispatch(action: A): void {
    const { state, events } = this.reducer(this.state, action);
    this.state = state;
    events.forEach((e) => this.log.record(e));
    this.listeners.forEach((fn) => fn(state, action.type));
  }

  change(change: Change): void {
    this.state = this.changer(this.state, change);
    this.log.record({ kind: "page_change", detail: { change: change.type } });
    this.listeners.forEach((fn) => fn(this.state, "change"));
  }
}

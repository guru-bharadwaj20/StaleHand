// Everything the agent does in an app is logged here; the Python side reads it to score the episode.

export interface ActionEvent {
  kind: string;
  itemId?: string;
  commit?: boolean; // true for the action that completes the task (send, add to cart, ...)
  detail?: Record<string, unknown>;
}

export interface LoggedEvent extends ActionEvent {
  seq: number;
  t: number;
}

export class ActionLog {
  private readonly items: LoggedEvent[] = [];

  constructor(private readonly clock: () => number = () => Date.now()) {}

  record(event: ActionEvent): LoggedEvent {
    const logged = { ...event, seq: this.items.length, t: this.clock() };
    this.items.push(logged);
    return logged;
  }

  events(): LoggedEvent[] {
    return [...this.items];
  }

  commits(): LoggedEvent[] {
    return this.items.filter((e) => e.commit);
  }
}

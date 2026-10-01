// Tiny DOM helpers shared by the app renderers.

export function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, text?: string) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

export function button(role: string, label: string, onClick: () => void): HTMLElement {
  const b = el("button", { "data-role": role, type: "button" }, label);
  b.addEventListener("click", onClick);
  return b;
}

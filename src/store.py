"""Simple in-memory store seeded from markdown input files."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOALS_PATH = ROOT / "inputs" / "goals.md"
CONSTRAINTS_PATH = ROOT / "inputs" / "constraints.md"


def _parse_markdown_list(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped.startswith("* "):
            items.append(stripped[2:].strip())
    return items


def _load_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    return _parse_markdown_list(path.read_text(encoding="utf-8"))


def _to_markdown(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) + ("\n" if items else "")


class PlannerStore:
    def __init__(self) -> None:
        self.goals: list[str] = _load_list(GOALS_PATH)
        self.constraints: list[str] = _load_list(CONSTRAINTS_PATH)

    def set_goals(self, goals: list[str]) -> list[str]:
        self.goals = [g.strip() for g in goals if g.strip()]
        GOALS_PATH.write_text(_to_markdown(self.goals), encoding="utf-8")
        return self.goals

    def set_constraints(self, constraints: list[str]) -> list[str]:
        self.constraints = [c.strip() for c in constraints if c.strip()]
        CONSTRAINTS_PATH.write_text(_to_markdown(self.constraints), encoding="utf-8")
        return self.constraints


store = PlannerStore()

import json
import os
from config import CATEGORY_FILTER


def load_universal_groups():
    """
    Load and normalize groups from JSON.

    Search order:
      - data/universal_groups.json
      - universal_groups.json
      - data/universal_group.json (fallback singular)
      - universal_group.json (fallback singular)
    Each entry may contain: link/url, category, priority.
    Applies optional CATEGORY_FILTER and sorts by priority.
    Duplicates are removed, preserving the highest priority instance.
    """

    candidate_paths = [
        os.path.join("data", "universal_groups.json"),
        "universal_groups.json",
        os.path.join("data", "universal_group.json"),
        "universal_group.json",
    ]

    groups = []
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    groups = json.load(f) or []
                break
            except Exception:
                return []

    if not groups:
        return []

    # Apply category filter if set
    if CATEGORY_FILTER:
        groups = [g for g in groups if (g.get("category", "") or "").strip().lower() == CATEGORY_FILTER]

    # Normalize, dedupe, prefer highest priority
    priority_rank = {"high": 1, "medium": 2, "low": 3}
    link_to_entry = {}
    for raw in groups:
        link = (raw.get("link") or raw.get("url") or "").strip()
        if not link:
            continue
        category = (raw.get("category", "") or "").strip()
        priority = (raw.get("priority", "medium") or "medium").strip().lower()
        entry = {"link": link, "category": category, "priority": priority}

        if link not in link_to_entry:
            link_to_entry[link] = entry
        else:
            # keep the one with higher priority (smaller rank)
            existing = link_to_entry[link]
            if priority_rank.get(priority, 99) < priority_rank.get(existing.get("priority", "medium"), 99):
                link_to_entry[link] = entry

    normalized = list(link_to_entry.values())
    normalized.sort(key=lambda g: priority_rank.get(g.get("priority", "medium"), 99))

    return normalized

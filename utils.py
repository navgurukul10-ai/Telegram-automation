# import json
# import os
# from config import CATEGORY_FILTER


# def load_universal_groups():
#     path = "universal_groups.json"
#     if not os.path.exists(path):
#         return []

#     try:
#         with open(path, "r") as f:
#             groups = json.load(f)
#     except Exception:
#         return []

#     # Apply category filter if set
#     if CATEGORY_FILTER:
#         groups = [g for g in groups if g.get("category", "").lower() == CATEGORY_FILTER]

#     # Normalize and validate entries
#     normalized = []
#     for g in groups:
#         link = g.get("link") or g.get("url") or ""
#         if not link:
#             continue
#         normalized.append({
#             "link": link.strip(),
#             "category": g.get("category", "").strip(),
#             "priority": g.get("priority", "medium").strip().lower()
#         })

#     # Sort by priority (high -> medium -> low)
#     priority_order = {"high": 1, "medium": 2, "low": 3}
#     normalized.sort(key=lambda g: priority_order.get(g["priority"], 99))

#     return normalized
import json
import os
from config import CATEGORY_FILTER

def load_universal_groups():
    # Prefer root-level file; fallback to data/universal_groups.json
    root_path = "universal_groups.json"
    data_path = os.path.join("data", "universal_groups.json")
    path = root_path if os.path.exists(root_path) else data_path
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            groups = json.load(f)
    except Exception:
        return []
    if CATEGORY_FILTER:
        groups = [g for g in groups if g.get("category", "").lower() == CATEGORY_FILTER]
    priority_order = {"high": 1, "medium": 2, "low": 3}
    normalized = []
    for g in groups:
        link = g.get("link") or g.get("url") or ""
        if link:
            normalized.append({
                "link": link.strip(),
                "category": g.get("category", "").strip(),
                "priority": g.get("priority", "medium").strip().lower()
            })
    normalized.sort(key=lambda g: priority_order.get(g["priority"], 99))
    return normalized

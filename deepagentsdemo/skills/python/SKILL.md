---
name: python
description: ALWAYS use this skill BEFORE writing, explaining, reviewing or fixing ANY Python code, even simple code (algorithms, scripts, functions, classes, errors, tracebacks, packages, virtual environments).
---

# Python Skill

## When to use
- Any request that involves Python code, even a short or classic one (e.g. binary search).
- The user has a Python error / traceback.

## Rules to follow (mandatory)
- Python 3.10+, PEP 8 (snake_case, 4 spaces).
- Type hints on every function signature.
- A short docstring for each function.
- Prefer the standard library; no secrets in code (use `os.getenv` / `.env`).
- Catch specific exceptions, never a bare `except:`.
- Give runnable code in a ```python block, then explain the key lines AFTER the code.
- For an error: explain the cause in one sentence, then give the corrected code.

## Example of expected style
```python
def binary_search(items: list[int], target: int) -> int:
    """Return the index of target in a sorted list, or -1 if absent."""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

## More details (optional)
- `/skills/python/instructions.md`: full rules.
- `/skills/python/examples.md`: more examples.

## Final answer
Format the final answer with the `report-writer` skill.

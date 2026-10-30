# Python - Examples

## Example 1 - Write a function
**User:** Write a function that counts the words in a text file.

**Answer:**
```python
from pathlib import Path
from collections import Counter

def count_words(path: str) -> Counter[str]:
    """Return the number of occurrences of each word in a text file."""
    text = Path(path).read_text(encoding="utf-8").lower()
    return Counter(text.split())
```
- `Path(...).read_text` opens and closes the file automatically.
- `Counter` counts each word in one line.

## Example 2 - Fix an error
**User:** `KeyError: 'OPENAI_API_KEY'`

**Answer:** The environment variable does not exist. Load the `.env` file and use `os.getenv`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise RuntimeError("OPENAI_API_KEY is missing in .env")
```

# Python - Instructions

## Code style
- Python 3.10+, follow PEP 8 (snake_case, 4 spaces, max ~100 chars per line).
- Add type hints on function signatures.
- Short docstring for public functions.
- Prefer the standard library before adding a dependency.

## Good practices
- Use `pathlib` for paths, `with` for files, f-strings for formatting.
- Catch specific exceptions (`except ValueError:`), never a bare `except:`.
- No secrets in code: read them with `os.getenv` / `.env` (python-dotenv).
- Use a virtual environment (`python -m venv .venv`) and a `requirements.txt`.

## Debugging an error
1. Read the last line of the traceback (exception type + message).
2. Find the line of the user's code in the traceback.
3. Explain the cause in one sentence, then give the corrected code.

## Answer format
- Always give runnable code in a ```python block.
- Explain the key lines after the code, not before.

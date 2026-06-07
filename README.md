# OpenTriviaDB

A MicroPython-compatible wrapper for the [Open Trivia DB](https://opentdb.com/) API.

This is a fork of [parafoxia/opentriviadb](https://github.com/parafoxia/opentriviadb) rewritten for use on microcontrollers running MicroPython. The async/aiohttp-based API has been replaced with synchronous `urequests` calls, and dependencies on CPython-only standard library modules (`asyncio`, `dataclasses`, `enum`, `typing`) have been removed.

This is an unofficial wrapper, and is not affiliated with [PIXELTAIL GAMES LLC.](https://www.pixeltailgames.com/)

## Installation

### On a MicroPython device (via mpremote mip)

```sh
mpremote mip install github:ghostdisco/open-trivia-db
```

This installs the `opentriviadb` package and its `urequests` dependency directly onto the device.

### For desktop CPython (development / testing)

```sh
pip install requests
pip install -e .
```

Or install the built wheel:

```sh
pip install dist/opentriviadb-*.whl
```

Use `make build` to produce the wheel (see [Development](#development) below).

## Usage

Create a client and fetch questions:

```python
from opentriviadb import Client, Category

client = Client()

questions = client.round(
    amount=10,
    category=Category.SCIENCE_COMPUTERS,
    difficulty="easy",
    type="multiple",
)

for q in questions:
    print(q.question)
    for i, opt in enumerate(q.options, 1):
        print(f"  {i}. {opt}")
```

### Session tokens

Session tokens let the API track which questions you have already received, preventing duplicates within a session.

```python
client = Client()
client.request_token()   # token stored on client.token

# Reset when all questions for your filter have been exhausted:
client.reset_token()
```

### `Question` objects

| Attribute | Type | Description |
|---|---|---|
| `category` | `str` | Question category |
| `type` | `str` | `"multiple"` or `"boolean"` |
| `difficulty` | `str` | `"easy"`, `"medium"`, or `"hard"` |
| `question` | `str` | The question text |
| `correct_answer` | `str` | The correct answer |
| `incorrect_answers` | `list` | List of wrong answers |

| Method / property | Returns | Description |
|---|---|---|
| `options` | `list` | All answers shuffled (or `["True", "False"]` for boolean) |
| `answer(option)` | `bool` | `True` if `option` matches the correct answer |

### `Category` values

```python
Category.GENERAL_KNOWLEDGE
Category.ENTERTAINMENT_BOOKS
Category.ENTERTAINMENT_FILM
Category.ENTERTAINMENT_MUSIC
Category.ENTERTAINMENT_MUSICALS_AND_THEATRES
Category.ENTERTAINMENT_TELEVISION
Category.ENTERTAINMENT_VIDEO_GAMES
Category.ENTERTAINMENT_BOARD_GAMES
Category.SCIENCE_AND_NATURE
Category.SCIENCE_COMPUTERS
Category.SCIENCE_MATHEMATICS
Category.MYTHOLOGY
Category.SPORTS
Category.GEOGRAPHY
Category.HISTORY
Category.POLITICS
Category.ART
Category.CELEBRITIES
Category.ANIMALS
Category.VEHICLES
Category.ENTERTAINMENT_COMICS
Category.SCIENCE_GADGETS
Category.ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA
Category.ENTERTAINMENT_CARTOON_AND_ANIMATIONS
```

## Development

A `Makefile` is included for common tasks:

```sh
make build    # Build a .whl and sdist in dist/
make test     # Run the sanity-check test against the live API
make clean    # Remove build artefacts
```

## License

The OpenTriviaDB module for Python is licensed under the [BSD 3-Clause License](https://github.com/ghostdisco/open-trivia-db/blob/main/LICENSE).

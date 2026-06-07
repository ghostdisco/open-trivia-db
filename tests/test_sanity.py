"""Sanity-check tests against the live Open Trivia DB API.

Run with:  python tests/test_sanity.py
Or via:    make test
"""

import sys
import time
import traceback

# The API enforces a rate limit of roughly one request per 5 seconds.
_RATE_LIMIT_DELAY = 5.5

try:
    import requests as _req  # noqa: F401 — verify dep is present
except ImportError:
    print("ERROR: 'requests' is not installed. Run: pip install requests")
    sys.exit(1)

from opentriviadb import Client, Category
from opentriviadb.errors import OpenTriviaError
from opentriviadb.questions import Question

PASS = "PASS"
FAIL = "FAIL"


def run(name, fn):
    time.sleep(_RATE_LIMIT_DELAY)
    try:
        fn()
        print(f"  [{PASS}] {name}")
        return True
    except Exception as exc:
        print(f"  [{FAIL}] {name}")
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_basic_round():
    client = Client()
    questions = client.round(amount=5)
    assert isinstance(questions, list), "round() must return a list"
    assert len(questions) == 5, f"expected 5 questions, got {len(questions)}"
    for q in questions:
        assert isinstance(q, Question)
        assert q.question
        assert q.correct_answer
        assert isinstance(q.incorrect_answers, list)


def test_category_filter():
    client = Client()
    questions = client.round(amount=3, category=Category.SCIENCE_COMPUTERS)
    assert len(questions) == 3
    for q in questions:
        assert "computer" in q.category.lower() or "science" in q.category.lower(), (
            f"unexpected category: {q.category}"
        )


def test_difficulty_filter():
    client = Client()
    questions = client.round(amount=3, difficulty="easy")
    for q in questions:
        assert q.difficulty == "easy", f"expected easy, got {q.difficulty}"


def test_boolean_type():
    client = Client()
    questions = client.round(amount=3, type="boolean")
    for q in questions:
        assert q.type == "boolean"
        assert q.options == ["True", "False"]


def test_multiple_type_options():
    client = Client()
    questions = client.round(amount=3, type="multiple")
    for q in questions:
        opts = q.options
        assert len(opts) == 4, f"expected 4 options, got {len(opts)}"
        assert q.correct_answer in opts


def test_answer_method():
    client = Client()
    questions = client.round(amount=3)
    for q in questions:
        assert q.answer(q.correct_answer) is True
        for wrong in q.incorrect_answers:
            assert q.answer(wrong) is False


def test_session_token():
    client = Client()
    token = client.request_token()
    assert isinstance(token, str) and token, "token should be a non-empty string"
    assert client.token == token
    client.reset_token()


def test_context_manager():
    with Client() as client:
        questions = client.round(amount=2)
    assert len(questions) == 2


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    ("Basic round (5 questions)", test_basic_round),
    ("Category filter (Science: Computers)", test_category_filter),
    ("Difficulty filter (easy)", test_difficulty_filter),
    ("Boolean question type", test_boolean_type),
    ("Multiple-choice options (4 per question)", test_multiple_type_options),
    ("answer() method correctness", test_answer_method),
    ("Session token request and reset", test_session_token),
    ("Context manager", test_context_manager),
]

if __name__ == "__main__":
    print("Running opentriviadb sanity checks against live API...\n")
    results = [run(name, fn) for name, fn in TESTS]
    total = len(results)
    passed = sum(results)
    failed = total - passed
    print(f"\n{passed}/{total} passed", end="")
    if failed:
        print(f", {failed} FAILED")
        sys.exit(1)
    else:
        print()

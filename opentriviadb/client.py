# Copyright (c) 2022-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Client interfaces for the OpenTriviaDB wrapper."""

import binascii

try:
    import urequests as _requests
except ImportError:
    import requests as _requests

from opentriviadb import BASE_URL, TOKEN_URL
from opentriviadb.errors import InvalidParameter, NoResults, RateLimitExceeded, TokenEmpty, TokenNotFound
from opentriviadb.questions import Question

EXCEPTIONS = [None, NoResults, InvalidParameter, TokenNotFound, TokenEmpty, RateLimitExceeded]


def _b64decode(s):
    data = s.encode("utf-8") if isinstance(s, str) else s
    return binascii.a2b_base64(data).decode("utf-8")


class Category:
    GENERAL_KNOWLEDGE = 9
    ENTERTAINMENT_BOOKS = 10
    ENTERTAINMENT_FILM = 11
    ENTERTAINMENT_MUSIC = 12
    ENTERTAINMENT_MUSICALS_AND_THEATRES = 13
    ENTERTAINMENT_TELEVISION = 14
    ENTERTAINMENT_VIDEO_GAMES = 15
    ENTERTAINMENT_BOARD_GAMES = 16
    SCIENCE_AND_NATURE = 17
    SCIENCE_COMPUTERS = 18
    SCIENCE_MATHEMATICS = 19
    MYTHOLOGY = 20
    SPORTS = 21
    GEOGRAPHY = 22
    HISTORY = 23
    POLITICS = 24
    ART = 25
    CELEBRITIES = 26
    ANIMALS = 27
    VEHICLES = 28
    ENTERTAINMENT_COMICS = 29
    SCIENCE_GADGETS = 30
    ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA = 31
    ENTERTAINMENT_CARTOON_AND_ANIMATIONS = 32


class Client:
    """A client for the Open Trivia API."""

    def __init__(self, token=None):
        self.token = token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def round(self, amount=10, category=None, difficulty=None, type=None):
        """Fetch a list of trivia questions.

        Parameters
        ----------
        amount : int
            Number of questions (max 50, default 10).
        category : Category attribute, optional
            A value from the Category class (e.g. Category.GENERAL_KNOWLEDGE).
        difficulty : str, optional
            "easy", "medium", or "hard".
        type : str, optional
            "multiple" or "boolean".

        Returns
        -------
        list of Question
        """
        url = (
            BASE_URL
            + "?amount=" + str(amount)
            + ("&category=" + str(category) if category is not None else "")
            + ("&difficulty=" + difficulty if difficulty else "")
            + ("&type=" + type if type else "")
            + "&encode=base64"
            + ("&token=" + self.token if self.token else "")
        )

        resp = _requests.get(url)
        data = resp.json()
        resp.close()

        code = data["response_code"]
        if code != 0:
            raise EXCEPTIONS[code]()

        return [
            Question(
                _b64decode(r["category"]),
                _b64decode(r["type"]),
                _b64decode(r["difficulty"]),
                _b64decode(r["question"]),
                _b64decode(r["correct_answer"]),
                [_b64decode(i) for i in r["incorrect_answers"]],
            )
            for r in data["results"]
        ]

    def request_token(self):
        """Request a session token from the API.

        Returns
        -------
        str
            The session token (also stored as self.token).
        """
        resp = _requests.get(TOKEN_URL + "?command=request")
        data = resp.json()
        resp.close()
        self.token = data["token"]
        return self.token

    def reset_token(self):
        """Reset the session token."""
        if self.token:
            resp = _requests.get(TOKEN_URL + "?command=reset&token=" + self.token)
            resp.close()

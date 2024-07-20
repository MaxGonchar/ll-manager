from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Role(Enum):
    SUPER_ADMIN = "super-admin"
    ADMIN = "admin"
    SELF_EDUCATED = "self-educated"

    @classmethod
    def all_(cls) -> List[str]:
        return [item.value for item in cls]


class MessageStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


SUCCESS = "success"
WARNING = "warning"
DANGER = "danger"

WORD_UPDATED = "Word updated"

LLIST_SIZE_DESCRIPTION = "Number of expressions in the learn list"
PRACTICE_COUNT_THRESHOLD_DESCRIPTION = "The minimum number of practice events, when the expression can be considered to be removed from the learn list."
KNOWLEDGE_LEVEL_THRESHOLD_DESCRIPTION = "The percents of right answers, when the expression can be considered to be removed from the learn list."


class Tags(Enum):
    GRAMMAR = "grammar"
    ADVERB = "adverb"
    NOUN = "noun"
    VERB = "verb"
    PHRASE = "phrase"
    CONJUNCTION = "conjunction"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    ADJECTIVE = "adjective"
    INTERJECTION = "interjection"
    IDIOM = "idiom"
    PHRASAL_VERB = "phrasal verb"
    PROVERB = "proverb"

    @classmethod
    def list_(cls) -> List[str]:
        return [item.value for item in cls]


@dataclass
class ComplexTag:
    display: str
    key: str


class GrammarTag(Enum):
    VERB_PATTERN = ComplexTag("verb pattern", "verb_pattern")

    @classmethod
    def new_from_display(cls, display_name: str) -> Optional["GrammarTag"]:
        for instance in cls:
            if instance.display == display_name:
                return instance

    @classmethod
    def new_from_key(cls, key: str) -> Optional["GrammarTag"]:
        for instance in cls:
            if instance.key == key:
                return instance

    @classmethod
    def displays(cls):
        return [i.display for i in cls]

    @property
    def key(self) -> str:
        return self.value.key

    @property
    def display(self) -> str:
        return self.value.display

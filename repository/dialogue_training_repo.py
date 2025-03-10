from typing import TypedDict


class DialogueListItemDict(TypedDict):
    id: str
    title: str
    description: str


class DialogueDict(TypedDict):
    id: str
    title: str
    description: str
    settings: dict
    dialogue: list[dict]
    expressions: list[dict]


class DialogueTrainingRepo:
    def get(self, user_id: str, dialogue_id: str | None = None) -> list[DialogueListItemDict] | DialogueDict:
        # if dialogue_id is None:
        # return list of dialogues
        # else:
        # return dialogue by id
        pass

    def create(self, user_id: str, dialogue: DialogueDict) -> str:
        # create dialogue
        pass

    def update(self, user_id: str, dialogue: DialogueDict) -> None:
        # update dialogue
        pass

    def delete(self, user_id: str, dialogue_id: str) -> None:
        # delete dialogue
        pass

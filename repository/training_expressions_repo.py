from dataclasses import dataclass
from dao.daily_training_dao import (
    DailyTrainingLearnListItemDict,
    DailyTrainingDAO,
)
from dao.user_expressions_dao import UserExpressionsDAO
from extensions import db
from models.models import UserExpression
from sqlalchemy.orm import Session


@dataclass
class DailyTrainingLearnListItem:
    expression_id: str
    position: int
    practice_count: int
    knowledge_level: float
    last_practice_time: str | None

    # @classmethod
    # def new_from_expression_id(
    #     cls, expression_id: str
    # ) -> "DailyTrainingLearnListItem":
    #     return cls(
    #         expression_id=expression_id,
    #         position=0,
    #         practice_count=0,
    #         knowledge_level=0,
    #         last_practice_time=None,
    #     )

    # def serialize(self) -> DailyTrainingLearnListItemDict:
    #     return {
    #         "expressionId": self.expression_id,
    #         "knowledgeLevel": self.knowledge_level,
    #         "position": self.position,
    #         "practiceCount": self.practice_count,
    #         "lastPracticeTime": self.last_practice_time,
    #     }


@dataclass
class DailyTrainingLearnList:
    learn_list: list[DailyTrainingLearnListItem]

    # def __len__(self):
    #     return len(self.learn_list)

    # def __iter__(self):
    #     return iter(self.learn_list)

    # def insert(self, item: DailyTrainingLearnListItem) -> None:
    #     item.position = max(0, item.position) and min(len(self), item.position)
    #     self.learn_list.insert(item.position, item)

    def get_first_items_ids(self, amount: int) -> list[str]:
        return [item.expression_id for item in self.learn_list[:amount]]

    # def pop_item_by_id(
    #     self, item_id: str
    # ) -> DailyTrainingLearnListItem | None:
    #     for i, item in enumerate(self.learn_list):
    #         if item.expression_id == item_id:
    #             return self.learn_list.pop(i)

    # def serialize(self) -> list[DailyTrainingLearnListItemDict]:
    #     return [item.serialize() for item in self.learn_list]

    def get_item_ids(self) -> list[str]:
        return [item.expression_id for item in self.learn_list]

    # def get_as_dict_by_item_id(self) -> dict[str, DailyTrainingLearnListItem]:
    #     return {item.expression_id: item for item in self.learn_list}


class DailyTrainingRepo:
    def __init__(
        self,
        user_id: str,
        session: Session = db.session,
        daily_training_dao: DailyTrainingDAO = DailyTrainingDAO,
        user_expressions_dao: UserExpressionsDAO = UserExpressionsDAO,
    ):
        self.user_id = user_id
        self.session: Session = session
        self.daily_training_dao: DailyTrainingDAO = daily_training_dao
        self.user_expressions_dao: UserExpressionsDAO = user_expressions_dao
        self._training_list = self._init_training_list()

    def _init_training_list(self):
        daily_training_data = self.daily_training_dao(
            self.user_id, self.session
        ).get()
        training_list = [
            DailyTrainingLearnListItem(
                expression_id=item["expressionId"],
                position=item["position"],
                practice_count=item["practiceCount"],
                knowledge_level=item["knowledgeLevel"],
                last_practice_time=item["lastPracticeTime"],
            )
            for item in daily_training_data["learning_list"]
        ]
        return DailyTrainingLearnList(training_list)

    def get_next(self, amount: int) -> list[UserExpression]:
        # TODO: deal with expressions that can be deleted or deactivated.
        # ??? Mark as deleted and allow a user to remove from the list
        # ??? remove from the list here
        if user_expression_ids := self._training_list.get_first_items_ids(
            amount
        ):
            return self.user_expressions_dao(self.user_id, self.session).get(
                include=user_expression_ids
            )
        return []

    def get_list(self) -> list[UserExpression]:
        if ids := self._training_list.get_item_ids():
            return self.user_expressions_dao(self.user_id, self.session).get(
                include=ids
            )
        return []

    def add(self, expression):
        pass

    def delete(self, expression):
        pass

    def update(self, expressions: list):
        pass

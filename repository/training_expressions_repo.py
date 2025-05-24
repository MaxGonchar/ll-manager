from dataclasses import dataclass
from dao.daily_training_dao import (
    DailyTrainingDict,
    DailyTrainingLearnListItemDict,
    DailyTrainingDAO,
)
from dao.user_expressions_dao import UserExpressionsDAO
from extensions import db
from models.models import UserExpression
from sqlalchemy.orm import Session
from repository.exceptions import UserExpressionNotFoundException


@dataclass
class DailyTrainingLearnListItem:
    expression_id: str
    position: int
    practice_count: int
    knowledge_level: float
    last_practice_time: str | None

    @classmethod
    def new_from_expression_id(
        cls, expression_id: str
    ) -> "DailyTrainingLearnListItem":
        return cls(
            expression_id=expression_id,
            position=0,
            practice_count=0,
            knowledge_level=0,
            last_practice_time=None,
        )

    def serialize(self) -> DailyTrainingLearnListItemDict:
        return {
            "expressionId": self.expression_id,
            "knowledgeLevel": self.knowledge_level,
            "position": self.position,
            "practiceCount": self.practice_count,
            "lastPracticeTime": self.last_practice_time,
        }


@dataclass
class DailyTrainingLearnList:
    learn_list: list[DailyTrainingLearnListItem]

    # def __len__(self):
    #     return len(self.learn_list)

    # def __iter__(self):
    #     return iter(self.learn_list)

    def insert(self, item: DailyTrainingLearnListItem) -> None:
        item.position = max(0, item.position) and min(len(self), item.position)
        self.learn_list.insert(item.position, item)

    def get_first_items_ids(self, amount: int) -> list[str]:
        return [item.expression_id for item in self.learn_list[:amount]]

    # def pop_item_by_id(
    #     self, item_id: str
    # ) -> DailyTrainingLearnListItem | None:
    #     for i, item in enumerate(self.learn_list):
    #         if item.expression_id == item_id:
    #             return self.learn_list.pop(i)

    def serialize(self) -> list[DailyTrainingLearnListItemDict]:
        return [item.serialize() for item in self.learn_list]

    def get_item_ids(self) -> list[str]:
        return [item.expression_id for item in self.learn_list]

    # def get_as_dict_by_item_id(self) -> dict[str, DailyTrainingLearnListItem]:
    #     return {item.expression_id: item for item in self.learn_list}


class DailyTrainingData:
    def __init__(self, dt_data: DailyTrainingDict) -> None:
        self.llist = self._init_llist(dt_data)
        self.max_llist_size = dt_data["learnListSize"]
        self.practice_count_threshold = dt_data["practiceCountThreshold"]
        self.knowledge_level_threshold = dt_data["knowledgeLevelThreshold"]

    def _init_llist(
        self, dt_data: DailyTrainingDict
    ) -> DailyTrainingLearnList:
        llist = [
            DailyTrainingLearnListItem(
                expression_id=item["expressionId"],
                position=item["position"],
                practice_count=item["practiceCount"],
                knowledge_level=item["knowledgeLevel"],
                last_practice_time=item.get("lastPracticeTime"),
            )
            for item in dt_data["learning_list"]
        ]
        return DailyTrainingLearnList(llist)

    def get_next_expression_ids_to_train(self, amount: int) -> list[str]:
        return self.llist.get_first_items_ids(amount)

    # def get_next_expr_to_train_id(self) ->  str | None:
    #     return self.llist.get_first_item_id()

    # def pop_item_by_id(self, item_id: str) -> DailyTrainingLearnListItem:
    #     item = self.llist.pop_item_by_id(item_id)

    #     return item

    # def get_llist_size(self) -> int:
    #     return len(self.llist)

    # def insert_item(self, item: DailyTrainingLearnListItem) -> None:
    #     self.llist.insert(item)

    def serialize(self) -> DailyTrainingDict:
        return {
            "knowledgeLevelThreshold": self.knowledge_level_threshold,
            "learnListSize": self.max_llist_size,
            "practiceCountThreshold": self.practice_count_threshold,
            "learning_list": self.llist.serialize(),
        }

    def get_llist_expressions_ids(self) -> list[str]:
        return self.llist.get_item_ids()

    # def get_as_dict_by_id(self) -> dict[str, DailyTrainingLearnListItem]:
    #     return self.llist.get_as_dict_by_item_id()

    def add_item(self, item_id: str) -> None:
        item = DailyTrainingLearnListItem.new_from_expression_id(item_id)
        self.llist.insert(item)

    # def get_learn_list(self) -> list[DailyTrainingLearnListItem]:
    #     return self.llist.learn_list


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
        self.daily_training_data = DailyTrainingData(
            self.daily_training_dao(self.user_id, self.session).get()
        )

    def get_next(self, amount: int) -> list[UserExpression]:
        # TODO: deal with expressions that can be deleted or deactivated.
        # ??? Mark as deleted and allow a user to remove from the list
        # ??? remove from the list here
        if user_expression_ids := self.daily_training_data.get_next_expression_ids_to_train(
            amount
        ):
            return self.user_expressions_dao(self.user_id, self.session).get(
                include=user_expression_ids
            )
        return []

    def get_list(self) -> list[UserExpression]:
        if ids := self.daily_training_data.get_llist_expressions_ids():
            return self.user_expressions_dao(self.user_id, self.session).get(
                include=ids
            )
        return []

    def add(self, expression_id: str):
        # TODO: check if expression_id already exists in the list
        with self.session.begin():
            try:
                if self.user_expressions_dao(self.user_id, self.session).get(
                    include=[expression_id]
                ):
                    self.daily_training_data.add_item(expression_id)
                    self.daily_training_dao(self.user_id, self.session).put(
                        self.daily_training_data.serialize(), commit=False
                    )
                    self.session.commit()
                else:
                    raise UserExpressionNotFoundException(
                        f"User expression with id {expression_id} not found for user {self.user_id}"
                    )
            except Exception:
                self.session.rollback()
                raise

    def delete(self, expression):
        pass

    def update(self, expressions: list):
        pass

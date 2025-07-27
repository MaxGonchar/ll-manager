from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
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
from exercises.common import (
    calculate_knowledge_level,
    ExerciseExpressionsListItem,
    get_exercise_expressions_list_item,
)
from helpers.time_helpers import get_current_utc_time, string_to_datetime


class UpdateTrainedExpression(TypedDict):
    user_expression: UserExpression
    is_trained_successfully: bool


class DailyTrainingSettings(TypedDict):
    max_learn_list_size: int
    knowledge_level_threshold: float
    practice_count_threshold: int


class TrainingRepoABC(ABC):
    @abstractmethod
    def get_next(self, amount: int) -> list[UserExpression]:
        """Get next expressions to train."""
        pass

    @abstractmethod
    def get_by_id(self, expression_id: str) -> UserExpression | None:
        """Get expression by ID."""
        pass

    @abstractmethod
    def update_expressions(self, data: list[UpdateTrainedExpression]) -> None:
        """Update expressions training data according to was it trained successfully."""
        pass

    @abstractmethod
    def get_list(self) -> list[UserExpression]:
        """Get the list of expressions."""
        pass

    @abstractmethod
    def add(self, expression_id: str) -> None:
        """Add expression to the training list."""
        pass

    @abstractmethod
    def delete(self, expression_id: str) -> None:
        """Delete expression from the training list."""
        pass

    @abstractmethod
    def update_settings(self, settings: DailyTrainingSettings) -> None:
        """Update daily training settings."""
        pass

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the training list."""
        pass

    @abstractmethod
    def count_learn_list_items(self) -> int:
        """Count the number of items in the learn list."""
        pass

    @abstractmethod
    def is_expression_in_learn_list(self, expression_id: str) -> bool:
        """Check if an expression is in the learn list."""
        pass


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

    def __len__(self):
        return len(self.learn_list)

    def __iter__(self):
        return iter(self.learn_list)

    def insert(self, item: DailyTrainingLearnListItem) -> None:
        item.position = max(0, item.position) and min(len(self), item.position)
        self.learn_list.insert(item.position, item)

    def get_first_items_ids(self, amount: int) -> list[str]:
        return [item.expression_id for item in self.learn_list[:amount]]

    def pop_item_by_id(
        self, item_id: str
    ) -> DailyTrainingLearnListItem | None:
        for i, item in enumerate(self.learn_list):
            if item.expression_id == item_id:
                return self.learn_list.pop(i)

    def serialize(self) -> list[DailyTrainingLearnListItemDict]:
        return [item.serialize() for item in self.learn_list]

    def get_item_ids(self) -> list[str]:
        return [item.expression_id for item in self.learn_list]

    def get_as_dict_by_item_id(self) -> dict[str, DailyTrainingLearnListItem]:
        return {item.expression_id: item for item in self.learn_list}


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

    def pop_item_by_id(self, item_id: str) -> DailyTrainingLearnListItem:
        return self.llist.pop_item_by_id(item_id)

    def get_llist_size(self) -> int:
        return len(self.llist)

    def insert_item(self, item: DailyTrainingLearnListItem) -> None:
        self.llist.insert(item)

    def serialize(self) -> DailyTrainingDict:
        return {
            "knowledgeLevelThreshold": self.knowledge_level_threshold,
            "learnListSize": self.max_llist_size,
            "practiceCountThreshold": self.practice_count_threshold,
            "learning_list": self.llist.serialize(),
        }

    def get_llist_expressions_ids(self) -> list[str]:
        return self.llist.get_item_ids()

    def get_as_dict_by_id(self) -> dict[str, DailyTrainingLearnListItem]:
        return self.llist.get_as_dict_by_item_id()

    def add_item(self, item_id: str) -> None:
        item = DailyTrainingLearnListItem.new_from_expression_id(item_id)
        self.llist.insert(item)

    # def get_learn_list(self) -> list[DailyTrainingLearnListItem]:
    #     return self.llist.learn_list


class DailyTrainingRepo(TrainingRepoABC):
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

    def get_list(self) -> list[ExerciseExpressionsListItem]:
        if ids := self.daily_training_data.get_llist_expressions_ids():
            user_expressions = self.user_expressions_dao(
                self.user_id, self.session
            ).get(include=ids)
            learn_list = self.daily_training_data.get_as_dict_by_id()
            return [
                get_exercise_expressions_list_item(
                    expr_id=str(expr.expression_id),
                    expression=expr.expression.expression,
                    knowledge_level=learn_list[
                        str(expr.expression_id)
                    ].knowledge_level,
                    practice_count=learn_list[
                        str(expr.expression_id)
                    ].practice_count,
                    last_practice_time=string_to_datetime(
                        learn_list[str(expr.expression_id)].last_practice_time
                    )
                    if learn_list[str(expr.expression_id)].last_practice_time
                    is not None
                    else None,
                )
                for expr in user_expressions
            ]
        return []

    def add(self, expression_id: str):

        if (
            expression_id
            in self.daily_training_data.get_llist_expressions_ids()
        ):
            return

        try:
            if self._get_user_expression_by_id(expression_id):
                self.daily_training_data.add_item(expression_id)
                self._store_daily_training_data(commit=False)
                self.session.commit()
            else:
                raise UserExpressionNotFoundException(
                    f"User expression with id {expression_id} not found for user {self.user_id}"
                )
        except Exception:
            self.session.rollback()
            raise

    def delete(self, expression_id: str):
        self.daily_training_data.pop_item_by_id(expression_id)
        self._refresh_llist()

    def update_expressions(self, data: list[UpdateTrainedExpression]) -> None:
        for item in data:
            self._update_item_training_data(
                str(item["user_expression"].expression_id),
                item["is_trained_successfully"],
            )

        updated_user_expressions = self._update_user_expressions_training_data(
            data
        )

        try:
            self._refresh_llist(commit=False)
            self.user_expressions_dao(self.user_id, self.session).bulk_update(
                updated_user_expressions
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def refresh(self):
        self._refresh_llist()

    def get_by_id(self, expression_id: str) -> UserExpression | None:
        if user_expr := self._get_user_expression_by_id(expression_id):
            return user_expr[0]
        return None

    def update_settings(self, settings: DailyTrainingSettings) -> None:
        self.daily_training_data.max_llist_size = settings[
            "max_learn_list_size"
        ]
        self.daily_training_data.knowledge_level_threshold = settings[
            "knowledge_level_threshold"
        ]
        self.daily_training_data.practice_count_threshold = settings[
            "practice_count_threshold"
        ]
        self._refresh_llist()

    def _get_user_expression_by_id(
        self, expression_id: str
    ) -> UserExpression | None:
        return self.user_expressions_dao(self.user_id, self.session).get(
            include=[expression_id]
        )

    def _update_item_training_data(
        self, user_expression_id: str, success: bool
    ) -> None:
        llist_item = self.daily_training_data.pop_item_by_id(
            user_expression_id
        )
        llist_item.knowledge_level = calculate_knowledge_level(
            llist_item.knowledge_level, llist_item.practice_count, success
        )
        llist_item.practice_count += 1
        llist_item.position += 1 if success else -1
        llist_item.last_practice_time = get_current_utc_time()
        self.daily_training_data.insert_item(llist_item)

    def _update_user_expressions_training_data(
        self, data: list[UpdateTrainedExpression]
    ) -> list[UserExpression]:
        updated_expressions = []
        for item in data:
            user_expression = item["user_expression"]
            user_expression.knowledge_level = calculate_knowledge_level(
                user_expression.knowledge_level,
                user_expression.practice_count,
                item["is_trained_successfully"],
            )
            user_expression.practice_count += 1
            current_time = get_current_utc_time()
            user_expression.last_practice_time = current_time
            user_expression.updated = current_time
            updated_expressions.append(user_expression)
        return updated_expressions

    def _refresh_llist(self, commit: bool = True):
        # TODO: add "updated" flag to not update daily training data if nothing changed
        self._remove_fully_trained_expressions()
        self._add_new_expressions_if_vacancies()
        self._store_daily_training_data(commit)

    def count_learn_list_items(self) -> int:
        return self.daily_training_data.get_llist_size()

    def is_expression_in_learn_list(self, expression_id: str) -> bool:
        return (
            expression_id
            in self.daily_training_data.get_llist_expressions_ids()
        )

    def _remove_fully_trained_expressions(self):
        item_ids_to_remove = [
            item.expression_id
            for item in self.daily_training_data.llist
            if self._should_be_removed(item)
        ]

        for id_ in item_ids_to_remove:
            self.daily_training_data.pop_item_by_id(id_)

    def _should_be_removed(self, item: DailyTrainingLearnListItem) -> bool:
        return (
            item.knowledge_level
            >= self.daily_training_data.knowledge_level_threshold
            and item.practice_count
            >= self.daily_training_data.practice_count_threshold
        )

    def _add_new_expressions_if_vacancies(self):
        vacancies = (
            self.daily_training_data.max_llist_size
            - self.daily_training_data.get_llist_size()
        )
        if vacancies > 0:
            llist_expr_ids = (
                self.daily_training_data.get_llist_expressions_ids()
            )
            ids_to_add = [
                str(expr.expression_id)
                for expr in self.user_expressions_dao(
                    self.user_id, self.session
                ).get(exclude=llist_expr_ids, limit=vacancies)
            ]

            for id_ in reversed(ids_to_add):
                self.daily_training_data.add_item(id_)

    def _store_daily_training_data(self, commit: bool = True):
        self.daily_training_dao(self.user_id, self.session).put(
            self.daily_training_data.serialize(), commit=commit
        )

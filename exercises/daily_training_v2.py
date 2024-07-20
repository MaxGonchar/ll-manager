from dataclasses import dataclass
from typing import Dict, List, Optional
from models.models import UserExpression

from exercises.common import (
    ChallengeDict,
    ChallengeSolutionDict,
    ExerciseExpressionsListItem,
    get_challenge_object,
    is_answer_correct,
    get_challenge_solution_object,
    get_exercise_expressions_list_item,
)
from repository.user_expressions_repo import UserExpressionsRepo
from repository.daily_training_repo import (
    DailyTrainingRepo,
    DailyTrainingLearnListItemDict,
    DailyTrainingDict,
)
from helpers.time_helpers import get_current_utc_time, string_to_datetime
from exercises.exceptions import (
    ExpressionNotFoundException,
    LearnListItemNotFoundExpression,
)


@dataclass
class DailyTrainingLearnListItem:
    expression_id: str
    position: int
    practice_count: int
    knowledge_level: float
    last_practice_time: Optional[str]

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
    learn_list: List[DailyTrainingLearnListItem]

    def __len__(self):
        return len(self.learn_list)

    def __iter__(self):
        return iter(self.learn_list)

    def insert(self, item: DailyTrainingLearnListItem) -> None:
        item.position = max(0, item.position) and min(len(self), item.position)
        self.learn_list.insert(item.position, item)

    def get_first_item_id(self) -> Optional[str]:
        return self.learn_list[0].expression_id if self.learn_list else None

    def pop_item_by_id(
        self, item_id: str
    ) -> Optional[DailyTrainingLearnListItem]:
        for i, item in enumerate(self.learn_list):
            if item.expression_id == item_id:
                return self.learn_list.pop(i)

    def serialize(self) -> List[DailyTrainingLearnListItemDict]:
        return [item.serialize() for item in self.learn_list]

    def get_item_ids(self) -> List[str]:
        return [item.expression_id for item in self.learn_list]

    def get_as_dict_by_item_id(self) -> Dict[str, DailyTrainingLearnListItem]:
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

    def get_next_expr_to_train_id(self) -> Optional[str]:
        return self.llist.get_first_item_id()

    def pop_item_by_id(self, item_id: str) -> DailyTrainingLearnListItem:
        item = self.llist.pop_item_by_id(item_id)

        if not item:
            raise LearnListItemNotFoundExpression(
                f"Learn list item {item_id} not found"
            )

        return item

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

    def get_llist_expressions_ids(self) -> List[str]:
        return self.llist.get_item_ids()

    def get_as_dict_by_id(self) -> Dict[str, DailyTrainingLearnListItem]:
        return self.llist.get_as_dict_by_item_id()

    def add_item(self, item_id: str) -> None:
        item = DailyTrainingLearnListItem.new_from_expression_id(item_id)
        self.llist.insert(item)

    def get_learn_list(self) -> List[DailyTrainingLearnListItem]:
        return self.llist.learn_list


class DailyTraining:
    def __init__(self, user_id: str) -> None:
        self.dt_repo = DailyTrainingRepo(user_id)
        self.user_expr_repo = UserExpressionsRepo(user_id)
        self.dt_data = DailyTrainingData(self.dt_repo.get())

    def _get_expression_by_id(self, id_: str) -> UserExpression:
        expr = self.user_expr_repo.get_by_id(id_)

        if expr is None:
            raise ExpressionNotFoundException(f"Expression {id_} not found")
        return expr

    def get_challenge(self) -> Optional[ChallengeDict]:
        next_expr_id = self.dt_data.get_next_expr_to_train_id()

        if next_expr_id is None:
            return None

        expr = self._get_expression_by_id(next_expr_id)

        return get_challenge_object(expr.expression)

    def submit_challenge(
        self, expr_id: str, answer: str, hint: bool = False
    ) -> ChallengeSolutionDict:
        challenged_expr = self._get_expression_by_id(expr_id)
        correct = challenged_expr.expression

        if not hint:
            if is_answer_correct(correct.expression, answer):
                self._register_challenge(challenged_expr, successful=True)
            else:
                self._register_challenge(challenged_expr, successful=False)

        return get_challenge_solution_object(correct, answer)

    def get_learn_list_expressions(self) -> List[ExerciseExpressionsListItem]:
        llist_item_ids = self.dt_data.get_llist_expressions_ids()

        res = []

        if not llist_item_ids:
            return res

        expressions = self.user_expr_repo.get(include=llist_item_ids)
        expressions_dict = {
            str(expr.expression_id): expr for expr in expressions
        }

        for llist_expr in self.dt_data.get_learn_list():

            if not (expr := expressions_dict.get(llist_expr.expression_id)):
                raise ExpressionNotFoundException

            last_pract_time = (
                string_to_datetime(llist_expr.last_practice_time)
                if llist_expr.last_practice_time is not None
                else None
            )

            res.append(
                get_exercise_expressions_list_item(
                    llist_expr.expression_id,
                    expr.expression.expression,
                    llist_expr.knowledge_level,
                    llist_expr.practice_count,
                    last_pract_time,
                )
            )

        res.sort(key=lambda item: item["practice_count"], reverse=True)
        return res

    def add_item_to_learn_list(self, item_id: str) -> None:
        self.dt_data.add_item(item_id)
        self.dt_repo.put(self.dt_data.serialize())

    def remove_item_from_learn_list(self, item_id: str) -> None:
        # TODO: refresh after removing
        _ = self.dt_data.pop_item_by_id(item_id)
        self.dt_repo.put(self.dt_data.serialize())

    def update_settings(
        self, llist_size: int, practice_count: int, knowledge_level: float
    ) -> None:
        self.dt_data.max_llist_size = llist_size
        self.dt_data.practice_count_threshold = practice_count
        self.dt_data.knowledge_level_threshold = knowledge_level
        self._refresh_llist()
        self.dt_repo.put(self.dt_data.serialize())

    def refresh_learning_list(self) -> None:
        self._refresh_llist()
        self.dt_repo.put(self.dt_data.serialize())

    def count_learn_list_items(self):
        return self.dt_data.get_llist_size()

    def is_expression_in_learn_list(self, expr_id: str) -> bool:
        for item in self.dt_data.get_llist_expressions_ids():
            if item == expr_id:
                return True
        return False

    def _register_challenge(
        self, u_expr: UserExpression, successful: bool
    ) -> None:
        self._update_learn_list(str(u_expr.expression_id), successful)
        self._update_user_expression(u_expr, successful)

    def _update_learn_list(self, expr_id: str, successful: bool) -> None:
        llist_item = self.dt_data.pop_item_by_id(expr_id)

        llist_item.knowledge_level = self._calculate_knowledge_level(
            llist_item.knowledge_level,
            llist_item.practice_count,
            successful=successful,
        )
        llist_item.practice_count += 1

        if not self._should_be_removed(llist_item):
            shift = 1 if successful else -1
            llist_item.position += shift
            llist_item.last_practice_time = get_current_utc_time()
            self.dt_data.insert_item(llist_item)

        self._refresh_llist()
        self.dt_repo.put(self.dt_data.serialize())

    def _update_user_expression(
        self, u_expr: UserExpression, successful: bool
    ) -> None:
        u_expr.knowledge_level = self._calculate_knowledge_level(
            u_expr.knowledge_level,
            u_expr.practice_count,
            successful=successful,
        )
        u_expr.practice_count += 1
        u_expr.last_practice_time = get_current_utc_time()
        self.user_expr_repo.put(u_expr)

    @staticmethod
    def _calculate_knowledge_level(
        current_knowledge_level: float, practice_count: int, successful: bool
    ) -> float:
        success_score = 1 if successful else 0
        return ((current_knowledge_level * practice_count) + success_score) / (
            practice_count + 1
        )

    def _should_be_removed(self, item: DailyTrainingLearnListItem) -> bool:
        return (
            item.knowledge_level >= self.dt_data.knowledge_level_threshold
            and item.practice_count >= self.dt_data.practice_count_threshold
        )

    def _refresh_llist(self):
        # 1) remove items having knowledge level and practice count >= values in settings
        item_ids_to_remove = [
            item.expression_id
            for item in self.dt_data.llist
            if self._should_be_removed(item)
        ]

        for id_ in item_ids_to_remove:
            self.dt_data.pop_item_by_id(id_)

        # 2) add to llist if vacancies
        vacancies = self.dt_data.max_llist_size - self.dt_data.get_llist_size()
        if vacancies > 0:
            llist_expr_ids = self.dt_data.get_llist_expressions_ids()
            ids_to_add = [
                str(expr.expression_id)
                for expr in self.user_expr_repo.get(
                    exclude=llist_expr_ids, limit=vacancies
                )
            ]

            for id_ in reversed(ids_to_add):
                self.dt_data.insert_item(
                    DailyTrainingLearnListItem.new_from_expression_id(id_)
                )

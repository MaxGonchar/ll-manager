from typing import List, Optional, TypedDict
from extensions import db
from models.models import User
from repository.exceptions import UserNotFoundException


from sqlalchemy.orm import Session, attributes


class DailyTrainingLearnListItemDict(TypedDict):
    expressionId: str
    position: int
    practiceCount: int
    knowledgeLevel: float
    lastPracticeTime: Optional[str]


class DailyTrainingDict(TypedDict):
    learnListSize: int
    practiceCountThreshold: int
    knowledgeLevelThreshold: float
    learning_list: List[DailyTrainingLearnListItemDict]


class DailyTrainingDAO:
    def __init__(self, user_id: str, session: Session | None = None) -> None:
        self.session: Session = session or db.session
        self.user = self._get_user(user_id)

    def _get_user(self, user_id: str) -> User:
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundException("User not found")

        return user

    def get(self) -> DailyTrainingDict:
        dt_dict = self.user.properties["challenges"]["dailyTraining"]
        return dt_dict

    def put(self, dt_dict: DailyTrainingDict, commit: bool = True) -> None:
        self.user.properties["challenges"]["dailyTraining"] = dt_dict
        attributes.flag_modified(self.user, "properties")
        self.session.add(self.user)
        if commit:
            self.session.commit()

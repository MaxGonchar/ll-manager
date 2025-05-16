from uuid import uuid4
from typing import List, TypedDict
from typing_extensions import NotRequired

from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship, Mapped, attributes
from sqlalchemy import ForeignKey
from sqlalchemy.schema import CheckConstraint

from extensions import db


class UserLearnListItemType(TypedDict):
    expressionId: str
    position: int
    practiceCount: int
    knowledgeLevel: str


class DailyTrainingType(TypedDict):
    learnListSize: int
    practiceCountThreshold: int
    knowledgeLevelThreshold: int
    learning_list: List[UserLearnListItemType]


class UserChallengesType(TypedDict):
    dailyTraining: DailyTrainingType


class UserPropertiesType(TypedDict):
    nativeLang: str
    challenges: NotRequired[UserChallengesType]


tag_expression = db.Table(
    "tag_expression",
    db.Column("expression_id", ForeignKey("expressions.id"), primary_key=True),
    db.Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first = db.Column(db.String(20))
    last = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(70), nullable=False)
    properties = db.Column(JSON, nullable=False, default={})
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False)

    expressions: Mapped[List["UserExpression"]] = relationship(
        back_populates="user"
    )
    dialogues: Mapped[List["Dialogue"]] = relationship(back_populates="user")
    writings: Mapped[List["Writings"]] = relationship(back_populates="user")

    @property
    def native_lang(self):
        return self.properties["nativeLang"]

    def __repr__(self):
        return f"{self.id} - {self.email}"


class Expression(db.Model):
    __tablename__ = "expressions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    expression = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text)
    example = db.Column(db.Text)
    translations = db.Column(JSON, nullable=False, default={})
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    properties = db.Column(JSON, nullable=False, default={})

    users: Mapped[List["UserExpression"]] = relationship(
        back_populates="expression"
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary=tag_expression, back_populates="expressions"
    )

    context: Mapped[List["ExpressionContext"]] = relationship(
        back_populates="expression"
    )

    def __repr__(self):
        return f"{self.id} - {self.expression}"

    def translation(self, lang: str) -> str:
        return self.translations.get(lang) or "no translation"


class UserExpression(db.Model):
    __tablename__ = "user_expression"

    user_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
    )
    expression_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey("expressions.id"),
        primary_key=True,
        nullable=False,
    )
    active = db.Column(db.SmallInteger, nullable=False, default=1)
    last_practice_time = db.Column(db.DateTime)
    knowledge_level = db.Column(db.Numeric(8, 5), default=0)
    practice_count = db.Column(db.Integer, default=0)
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    properties = db.Column(JSON, nullable=False, default={})

    user: Mapped["User"] = relationship(back_populates="expressions")  # type: ignore
    expression: Mapped["Expression"] = relationship(back_populates="users")

    def __repr__(self):
        return f"user_id: {self.user_id}; expression_id: {self.expression_id}; active: {self.active}"


class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = (
        CheckConstraint(name="forbidden_tag", sqltext="tag <> 'untagged'"),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tag = db.Column(db.String(50), unique=True, nullable=False)
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)

    expressions: Mapped[List[Expression]] = relationship(
        secondary=tag_expression, back_populates="tags"
    )

    def __str__(self):
        return f"{self.id}-{self.tag}"

    def __repr__(self):
        return self.tag


class ExpressionContext(db.Model):
    __tablename__ = "expression_context"

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    expression_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey("expressions.id"),
        primary_key=True,
        nullable=False,
    )
    sentence = db.Column(db.Text, nullable=False)
    translation = db.Column(JSON, nullable=False, default={})
    template = db.Column(JSON, nullable=False)
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)

    expression: Mapped["Expression"] = relationship(back_populates="context")


class Dialogue(db.Model):
    __tablename__ = "dialogues"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = db.Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    properties = db.Column(JSON, nullable=False, default={})
    settings = db.Column(JSON, nullable=False)
    dialogues = db.Column(JSON, nullable=False, default=[])
    expressions = db.Column(JSON, nullable=False, default=[])
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="dialogues")

    def __repr__(self):
        return f"{self.id} - {self.title}"

    def update_expression_by_id(
        self, expression_id: str, status: str, comment: str
    ):
        for expression in self.expressions:
            if expression["id"] == expression_id:
                expression["status"] = status
                expression["comment"] = comment
                attributes.flag_modified(self, "expressions")
                break
        else:
            raise ValueError(
                f"Expression with id {expression_id} not found in the dialogue."
            )

    def remove_expression_by(self, expression_id: str):
        for expression in self.expressions:
            if expression["id"] == expression_id:
                self.expressions.remove(expression)
                attributes.flag_modified(self, "expressions")
                break
        else:
            raise ValueError(
                f"Expression with id {expression_id} not found in the dialogue."
            )

    def add_expressions(self, expressions: list[Expression]) -> None:
        for expression in expressions:
            self.expressions.append(
                {
                    "id": str(expression.id),
                    "expression": expression.expression,
                    "definition": expression.definition,
                    "status": "not_checked",
                }
            )
        attributes.flag_modified(self, "expressions")

    def add_message(
        self, message: str, role: str, comment: list[dict] | None = None
    ) -> None:
        message_to_add = {
            "id": len(self.dialogues) + 1,
            "role": role,
            "text": message,
        }
        if comment is not None:
            message_to_add["comment"] = comment

        self.dialogues.append(message_to_add)
        attributes.flag_modified(self, "dialogues")

    def get_dialogue_expression(self, expression_id: str) -> dict | None:
        for expression in self.expressions:
            if expression["id"] == expression_id:
                return expression
        return None

    def increase_trained_expressions_count(self) -> None:
        self.properties["trainedExpressionsCount"] += 1
        attributes.flag_modified(self, "properties")


class Writings(db.Model):
    __tablename__ = "writings"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = db.Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    properties = db.Column(JSON, nullable=False)
    writings = db.Column(JSON, nullable=False, default=[])
    expressions = db.Column(JSON, nullable=False, default=[])
    added = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="writings")

    def add_expressions(self, expressions: list[Expression]) -> None:
        for expression in expressions:
            self.expressions.append(
                {
                    "id": str(expression.id),
                    "expression": expression.expression,
                    "definition": expression.definition,
                    "status": "not_checked",
                }
            )
        attributes.flag_modified(self, "expressions")

    def get_expression(self, expression_id: str) -> dict | None:
        for expression in self.expressions:
            if expression["id"] == expression_id:
                return expression
        return None

    def remove_expression_by(self, expression_id: str):
        for expression in self.expressions:
            if expression["id"] == expression_id:
                self.expressions.remove(expression)
                attributes.flag_modified(self, "expressions")
                break
        else:
            raise ValueError(
                f"Expression with id {expression_id} not found in the writings."
            )

    def update_expression_by_id(
        self, expression_id: str, status: str, comment: str
    ):
        for expression in self.expressions:
            if expression["id"] == expression_id:
                expression["status"] = status
                expression["comment"] = comment
                attributes.flag_modified(self, "expressions")
                break
        else:
            raise ValueError(
                f"Expression with id {expression_id} not found in the writings."
            )

    def add_message(
        self, message: str, comment: list[dict] | None = None
    ) -> None:
        message_to_add = {
            "id": len(self.writings) + 1,
            "text": message,
        }
        if comment is not None:
            message_to_add["comment"] = comment

        self.writings.append(message_to_add)
        attributes.flag_modified(self, "writings")

from uuid import uuid4
from typing import List, TypedDict
from typing_extensions import NotRequired

from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship, Mapped
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

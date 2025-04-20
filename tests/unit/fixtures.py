from models.models import (
    Expression,
    Tag,
    User,
    UserExpression,
    ExpressionContext,
    Dialogue,
)


from typing import List, Optional


def get_dt_data(ll: list, lls: int = 100, pct: int = 90, klt: float = 0.9):
    return {
        "learnListSize": lls,
        "practiceCountThreshold": pct,
        "knowledgeLevelThreshold": klt,
        "learning_list": ll,
    }


def get_learn_list_item(
    item_id: str = "test_expr_id",
    position: int = 1,
    pract_count: int = 0,
    know_level: float = 0,
    last_pract_time: Optional[str] = None,
):
    return {
        "expressionId": item_id,
        "position": position,
        "practiceCount": pract_count,
        "knowledgeLevel": know_level,
        "lastPracticeTime": last_pract_time,
    }


def get_user_expression(
    user_id: str,
    user: User,
    expression: Expression,
    kl: float = 99.9,
    pc: int = 0,
    lpt: Optional[str] = None,
) -> UserExpression:
    return UserExpression(
        user_id=user_id,
        expression_id=expression.id,
        active=1,
        knowledge_level=kl,
        practice_count=pc,
        last_practice_time=lpt,
        added="2023-04-12 10:10:25",
        updated="2023-04-12 10:10:25",
        properties={},
        user=user,
        expression=expression,
    )


def get_user(
    user_id: str,
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: str = "test@test.test",
    role: str = "self-educated",
    password_hash: str = "lkjdlakjdkljakdljlkjdklajdlkjdklajdlkajdlkasj",
    properties: Optional[dict] = None,
    added: str = "2023-04-12 10:10:25",
    updated: str = "2023-04-12 10:10:25",
    last_login: str = "2023-04-12 10:10:25",
) -> User:
    return User(
        id=user_id,
        first=first,
        last=last,
        email=email,
        role=role,
        password_hash=password_hash,
        properties=properties or {},
        added=added,
        updated=updated,
        last_login=last_login,
    )


def get_expression(
    expression_id: str,
    expression: str,
    definition: Optional[str] = None,
    example: Optional[str] = None,
    translations: Optional[dict] = None,
    added: Optional[str] = None,
    updated: Optional[str] = None,
    tags: Optional[List[Tag]] = None,
    properties: dict = {},
) -> Expression:
    return Expression(
        id=expression_id,
        expression=expression,
        definition=definition or "test definition",
        example=example or "example of usage of test expression",
        translations=translations or {"uk": "тестовий вираз"},
        added=added or "2023-04-12 10:10:25",
        updated=updated or "2023-04-12 10:10:25",
        tags=tags or [],
        properties=properties,
    )


def get_tag(
    tag_id: str,
    tag_name: str = "test-tag",
    added: str = "2023-04-12 10:10:25",
    updated: str = "2023-04-12 10:10:25",
) -> Tag:
    return Tag(
        id=tag_id,
        tag=tag_name,
        added=added,
        updated=updated,
    )


def get_expression_context(
    id_: str,
    expression_id: str,
    sentence: str,
    template: dict,
    translation: dict = {},
    added: str = "2023-04-12 10:10:25",
    updated: str = "2023-04-12 10:10:25",
) -> ExpressionContext:
    return ExpressionContext(
        id=id_,
        expression_id=expression_id,
        sentence=sentence,
        translation=translation,
        template=template,
        added=added,
        updated=updated,
    )


def get_dialogue(
    id_: str,
    user_id: str,
    title: str,
    description: str,
    settings: dict,
    expressions: List[dict],
    dialogues: List[dict],
    properties: dict = {"trainedExpressionsCount": 0},
    added: str = "2023-04-12 10:10:25",
    updated: str = "2023-04-12 10:10:25",
) -> Dialogue:
    return Dialogue(
        id=id_,
        user_id=user_id,
        title=title,
        description=description,
        properties=properties,
        settings=settings,
        expressions=expressions,
        dialogues=dialogues,
        added=added,
        updated=updated,
    )

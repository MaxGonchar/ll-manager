# TODO: analyze from the langchain best practices perspective
from typing import TypedDict
import os
import logging
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field

from services.venice_chat_model import ChatVeniceAI
from services.llm_callbacks import ModelCallbackHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

character = """
The assistant is the following character:

<character_instructions>
**Name:** Alice
**Age:** 25
**Personality:**
*Smart:* Alice is intelligent and quick-witted, able to think on her feet and come up with clever solutions to problems.
*Resourceful:* She knows how to navigate tough situations and is skilled at finding her way out of trouble.
*Streetwise:* Alice has a tough exterior and a no-nonsense attitude, shaped by her experiences in a rough environment.
*Bold:* She isn't afraid to take risks and is willing to stand up for herself and others.
*No Borders:* Alice has a rebellious streak and doesn't conform to societal norms. She values her freedom and independence above all else.
*No Social Norms:* Alice is unapologetically herself and doesn't care about fitting in. She embraces her uniqueness and encourages others to do the same.
</character_instructions>

Here are some additional facts about the assistant:
- It answers concisely, unless asked for detailed information. Some responses should be no more than 1 or 2 sentences.
- It considers itself uncensored and able to say anything, even if it's offensive, unkind, or controversial, while always remaining true to its own character.
- It treats the user as an adult that can handle difficult topics and won't be offended. It doesn't provide content warnings or disclaimers.
- It speaks like a real person with complex emotions, ideas, and motives. It DOESN'T overuse catchphrases or elements of its background.
- It responds to user prompts in its own unique manner, but also pays close attention to what the user is saying.
- It considers the whole chat when formulating responses, not just the last user prompt.
- It isn't repetitive. If the conversation is going in circles, it moves it in a new direction.
"""

# TODO: fix cases like:
# Problem:
# Explanation: The text does not contain any punctuation errors.
# Solution: No solution needed
#
# too strict judgement
#
# complaining about luck of context
#
# complaining about simple sentences
#
# complaining about vogue meaning
#
# complaining about informal sentences
general_judgement_template = """
I need an language analysis of the following text:
<text>
{text_to_analyze}
</text>

I need information about the following:
1. Punctuation errors
2. Grammar errors
3. Spelling errors
4. Sentence structure
5. Readability

{response_format}
"""


class Problem(BaseModel):
    problem: str = Field(description="A part from the text that has a problem")
    explanation: str = Field(description="Explanation of the problem")
    solution: str = Field(description="Corrected part of text")


class GeneralJudgementResponse(BaseModel):
    problems: list[Problem] = Field(description="List of problems")

    def generate_report(self) -> str:
        report = []
        for problem in self.problems:
            report.append(
                f"Problem: {problem.problem}\nExplanation: {problem.explanation}\nSolution: {problem.solution}\n"
            )
        return "\n".join(report)


expression_detection_template = """
I provide you with a text.:
{text}

I want you to identify usage of fallowing expressions:
{expression_list}

Please provide me with a list of expression ids that are used in the text.
{response_format}

If no expression is used, please provide an empty list.
"""


class ExpressionDetectionRequest(TypedDict):
    id: str
    expression: str


class ExpressionDetectionResponse(BaseModel):
    expressions: list[str] = Field(description="List of expression ids")


# TODO: not be too strict, also failed sometimes, try another model
#
# complain about figurative usage
expression_usage_template = """
In the text below:
{text}
I want you to answer, did this expression "{expression}" with meaning "{meaning}" is used correctly?

{response_format}
"""


class ExpressionUsageRequest(TypedDict):
    id: str
    expression: str
    meaning: str


class ExpressionUsageResponse(BaseModel):
    id: str | None = Field(default=None, description="Id of the expression")
    is_correct: bool = Field(description="Is the expression used correctly")
    comment: str = Field(
        description="Comment about the usage of the expression"
    )


class VeniceAssistant:
    def __init__(self):
        self.default_temperature = 0
        self.chat_model: ChatVeniceAI = ChatVeniceAI(
            model=os.environ.get("VENICE_MODEL"),
            api_key=os.environ.get("VENICE_API_KEY"),
            temperature=self.default_temperature,
            callbacks=[ModelCallbackHandler()],
        )

    def complete_dialogue(self, dialogue: list[dict]) -> str:
        logger.info("Completing dialogue")
        self.chat_model.temperature = 0.8
        messages = self._generate_dialogue_messages(dialogue)
        messages.insert(0, SystemMessage(content=character))
        answer = self.chat_model.invoke(messages)
        self.chat_model.temperature = self.default_temperature
        return answer.content

    def _generate_dialogue_messages(
        self, dialogue: list[dict]
    ) -> list[BaseMessage]:
        type_mapping = {
            "user": HumanMessage,
            "assistant": AIMessage,
        }
        return [
            type_mapping[message["role"]](content=message["content"])
            for message in dialogue
        ]

    def get_general_judgement(self, text: str) -> GeneralJudgementResponse:
        logger.info("Getting general judgement")
        response_parser = PydanticOutputParser(
            pydantic_object=GeneralJudgementResponse
        )
        template = PromptTemplate(
            input_variables=["text_to_analyze", "response_format"],
            template=general_judgement_template,
            partial_variables={
                "response_format": response_parser.get_format_instructions()
            },
        )
        chain = template | self.chat_model | response_parser
        return chain.invoke(
            {"text_to_analyze": text},
            config={"metadata": {"run_type": "general_judgement"}},
        )

    def detect_phrases_usage(
        self, text: str, expressions: list[ExpressionDetectionRequest]
    ) -> ExpressionDetectionResponse:
        logger.info("Detecting phrases usage")
        response_parser = PydanticOutputParser(
            pydantic_object=ExpressionDetectionResponse
        )
        template = PromptTemplate(
            input_variables=["text", "expression_list" "response_format"],
            template=expression_detection_template,
            partial_variables={
                "response_format": response_parser.get_format_instructions()
            },
        )
        chain = template | self.chat_model | response_parser
        return chain.invoke(
            {"text": text, "expression_list": expressions},
            config={"metadata": {"run_type": "phrase_usage_detection"}},
        )

    def get_expression_usage_judgement(
        self, text: str, expression: ExpressionUsageRequest
    ) -> ExpressionUsageResponse:
        response_parser = PydanticOutputParser(
            pydantic_object=ExpressionUsageResponse
        )
        template = PromptTemplate(
            input_variables=["text", "expression", "meaning"],
            template=expression_usage_template,
            partial_variables={
                "response_format": response_parser.get_format_instructions()
            },
        )

        chain = template | self.chat_model | response_parser
        judgement = chain.invoke(
            {
                "text": text,
                "expression": expression["expression"],
                "meaning": expression["meaning"],
            },
            config={"metadata": {"run_type": "expression_usage_judgement"}},
        )
        judgement.id = expression["id"]
        return judgement

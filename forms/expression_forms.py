from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from constants import GrammarTag, Tags


class PostExpressionForm(FlaskForm):
    expression = StringField("expression", validators=[DataRequired()])
    definition = TextAreaField("definition", validators=[DataRequired()])
    translation = StringField("translation", validators=[DataRequired()])
    example = TextAreaField("example", validators=[DataRequired()])

    grammar = TextAreaField("grammar")
    grammar_tag = SelectField("grammar tag", choices=["", *GrammarTag.displays()])  # type: ignore

    tag_1 = SelectField("tag")
    tag_2 = SelectField("tag")
    tag_3 = SelectField("tag")
    tag_4 = SelectField("tag")
    tag_5 = SelectField("tag")

    def __init__(self, tags_names: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        tags_names = [""] + tags_names
        self.tag_1.choices = tags_names  # type: ignore
        self.tag_2.choices = tags_names  # type: ignore
        self.tag_3.choices = tags_names  # type: ignore
        self.tag_4.choices = tags_names  # type: ignore
        self.tag_5.choices = tags_names  # type: ignore

    def validate_grammar(self, field):
        if Tags.GRAMMAR.value in self.all_tags and not self.grammar.data:
            field.errors += (
                ValidationError(
                    "If expression has tag 'grammar', 'grammar' field can be empty"
                ),
            )

    def validate_grammar_tag(self, field):
        if Tags.GRAMMAR.value in self.all_tags and not self.grammar_tag.data:
            field.errors += (
                ValidationError(
                    "If expression has tag 'grammar', 'grammar_tag' field can be empty"
                ),
            )

    def validate_tag_1(self, field):
        self._validate_at_least_one_tag_filled(field)
        self._validate_tags_uniqueness(field)

    def _validate_tags_uniqueness(self, field):
        if len(self.all_tags) != len(set(self.all_tags)):
            field.errors += (ValidationError("Tags should be unique"),)

    def _validate_at_least_one_tag_filled(self, field):
        if not self.all_tags:
            field.errors += (ValidationError("Require at least one tag"),)

    @property
    def all_tags(self) -> List[str]:
        tag_fields = [
            self.tag_1,
            self.tag_2,
            self.tag_3,
            self.tag_4,
            self.tag_5,
        ]
        return [field.data for field in tag_fields if field.data]

    @property
    def all_fields(self):
        return list(self._fields.values())

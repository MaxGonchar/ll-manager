import difflib
import json
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError


class ExpressionSentenceForm(FlaskForm):
    sentence = TextAreaField("sentence", validators=[DataRequired()])
    translation = TextAreaField("translation", validators=[DataRequired()])
    template = TextAreaField("template", validators=[DataRequired()])

    def validate_template(self, field):
        try:
            template = json.loads(self.template.data)
            tpl = template["tpl"]
            values = template["values"]
        except Exception as e:
            field.errors += (ValidationError("Failed to parse template"),)
            print(repr(e))
            return

        if not values:
            field.errors += (ValidationError("Invalid template: no values"),)

        filled_template = tpl.format(*values)
        sentence = self.sentence.data
        if filled_template != sentence:
            field.errors += (ValidationError("Invalid template"),)
            print("INIT SENTENCE:", self.sentence.data)
            print("TPL SENTENCE:", tpl.format(*values))

            diff = difflib.ndiff(sentence, filled_template)
            print("".join(diff))

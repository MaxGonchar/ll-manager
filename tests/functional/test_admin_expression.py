from tests.functional.utils import FunctionalTestsHelper


class GetTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_admin_expression.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get(self):
        user_id = "2f732f36-c0f4-430f-921d-b62877891c80"
        session = {
            "user": "admin@test.com",
            "user_id": user_id,
        }
        self._set_session(**session)

        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"

        context = self._get_test_template_context(
            "GET",
            "admin/expression.html",
            f"/admin/expressions/{expr_id}",
        )

        self.assertEqual(expr_id, str(context["expression_id"]))

        form = context["form"]

        self.assertEqual("preceding", form.expression.data)
        self.assertEqual(
            "coming before something in order, position, or time",
            form.definition.data,
        )
        self.assertEqual("попередній", form.translation.data)
        self.assertEqual("preceding in sentence", form.example.data)

        self.assertEqual("", form.grammar.data)
        self.assertEqual("", form.grammar_tag.data)

        self.assertEqual("phrase", form.tag_1.data)
        self.assertEqual("noun", form.tag_2.data)
        self.assertEqual("", form.tag_3.data)
        self.assertEqual("", form.tag_4.data)
        self.assertEqual("", form.tag_5.data)


class UpdateTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_admin_expression.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_update(self):
        user_id = "2f732f36-c0f4-430f-921d-b62877891c80"
        session = {
            "user": "admin@test.com",
            "user_id": user_id,
        }
        self._set_session(**session)

        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"

        expression = "updated expression"
        definition = "updated definition"
        translation = "оновлений переклад"
        example = "updated example"
        grammar = "test grammar"
        grammar_tag = "verb pattern"
        tag_1 = "verb"
        tag_2 = "noun"
        tag_3 = "adverb"
        tag_4 = ""
        tag_5 = ""

        body = {
            "expression": expression,
            "definition": definition,
            "translation": translation,
            "example": example,
            "tag_1": tag_1,
            "tag_2": tag_2,
            "tag_3": tag_3,
            "tag_4": tag_4,
            "tag_5": tag_5,
            "grammar_tag": grammar_tag,
            "grammar": grammar,
        }

        self._get_test_template_context(
            "POST",
            "admin/expressions_list.html",
            f"/admin/expressions/{expr_id}",
            data=body,
            follow_redirects=True,
        )

        context = self._get_test_template_context(
            "GET",
            "admin/expression.html",
            f"/admin/expressions/{expr_id}",
        )

        self.assertEqual(expr_id, str(context["expression_id"]))

        form = context["form"]

        self.assertEqual(expression, form.expression.data)
        self.assertEqual(definition, form.definition.data)
        self.assertEqual(translation, form.translation.data)
        self.assertEqual(example, form.example.data)

        self.assertEqual(grammar, form.grammar.data)
        self.assertEqual(grammar_tag, form.grammar_tag.data)

        self.assertCountEqual(
            [
                tag_1,
                tag_2,
                tag_3,
                tag_4,
                tag_5,
            ],
            [
                form.tag_1.data,
                form.tag_2.data,
                form.tag_3.data,
                form.tag_4.data,
                form.tag_5.data,
            ],
        )

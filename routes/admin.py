import json

from flask import Blueprint, render_template, request, redirect, url_for

from helpers.rbac_helper import role_required
from constants import Role
from services.expression_service import ExpressionService
from forms.expression_forms import PostExpressionForm
from forms.expression_sentence import ExpressionSentenceForm
from services.tags_service import TagsService
from services.expression_context_service import ExpressionContextService
from constants import GrammarTag

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("", methods=["GET"])
def admin():
    role_required([Role.SUPER_ADMIN.value, Role.ADMIN.value])
    return render_template("admin/index.html")


@admin_bp.route("/expressions", methods=["GET", "POST"])
def expressions():
    role_required([Role.SUPER_ADMIN.value, Role.ADMIN.value])

    query_expression = ""
    expr_sv = ExpressionService()

    if request.method == "GET":
        exprs = expr_sv.get_expressions()
        return render_template(
            "admin/expressions_list.html",
            exprs=exprs,
            query_expression=query_expression,
        )

    exprs = expr_sv.search(request.form["query"])

    return render_template(
        "admin/expressions_list.html",
        exprs=exprs,
        query_expression=query_expression,
    )


# TODO: add pagination
@admin_bp.route("/expressions/<expression_id>", methods=["GET", "POST"])
def expression(expression_id: str):
    role_required([Role.SUPER_ADMIN.value, Role.ADMIN.value])

    expr_sv = ExpressionService()
    form = PostExpressionForm(TagsService().get_tag_names())

    if form.validate_on_submit():
        # add flash with message
        properties = {}
        if form.grammar.data and form.grammar_tag.data:
            if grammar_tag := GrammarTag.new_from_display(
                form.grammar_tag.data
            ):
                properties = {
                    "grammar": {grammar_tag.key: {"text": form.grammar.data}}
                }

        expr_sv.update_expression(
            expression_id=expression_id,
            expression=form.expression.data,  # type: ignore
            definition=form.definition.data,  # type: ignore
            translation=form.translation.data,  # type: ignore
            example=form.example.data,  # type: ignore
            tag_names=form.all_tags,
            properties=properties,
        )

        return redirect(url_for("admin.expressions"))

    expr = expr_sv.get_expression_by_id(expression_id)

    form.expression.data = expr["expression"]
    form.translation.data = expr["translation"]
    form.definition.data = expr["definition"]
    form.example.data = expr["example"]
    form.grammar.data = expr["grammar"] or ""
    form.grammar_tag.data = expr["grammar_tag"] or ""
    form.tag_1.data = expr["tag_1"]
    form.tag_2.data = expr["tag_2"] or ""
    form.tag_3.data = expr["tag_3"] or ""
    form.tag_4.data = expr["tag_4"] or ""
    form.tag_5.data = expr["tag_5"] or ""

    return render_template(
        "admin/expression.html", form=form, expression_id=expr["id"]
    )


# TODO: add delete, update expression
@admin_bp.route("/expressions/<expression_id>/sentences", methods=["GET"])
def expression_sentences(expression_id):
    role_required([Role.SUPER_ADMIN.value, Role.ADMIN.value])
    sentences = ExpressionContextService(expression_id).get_context()
    return render_template(
        "admin/sentences.html",
        sentences=sentences,
        expression_id=expression_id,
    )


@admin_bp.route(
    "/expressions/<expression_id>/sentences/add", methods=["GET", "POST"]
)
def add_expression_sentence(expression_id):
    role_required([Role.SUPER_ADMIN.value, Role.ADMIN.value])
    form = ExpressionSentenceForm()

    if form.validate_on_submit():
        ExpressionContextService(expression_id).post_context(
            form.sentence.data,
            form.translation.data,
            json.loads(form.template.data),
        )
        return redirect(
            url_for("admin.expression_sentences", expression_id=expression_id)
        )

    return render_template(
        "admin/add_sentence.html", form=form, expression_id=expression_id
    )

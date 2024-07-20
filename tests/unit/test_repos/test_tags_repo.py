from tests.unit.test_repos.utils import BaseRepoTestUtils
from repository.tags_repo import TagsRepo
from tests.unit.fixtures import get_tag
from models.models import Tag


class TagRepoTestHelper(BaseRepoTestUtils):
    def _assert_tag(self, expected: Tag, actual: Tag):
        self.assertEqual(expected.id, str(actual.id))
        self.assertEqual(expected.tag, actual.tag)
        self.assertEqual(
            expected.added, actual.added.strftime("%Y-%m-%d %H:%M:%S")
        )
        self.assertEqual(
            expected.updated, actual.updated.strftime("%Y-%m-%d %H:%M:%S")
        )


class GetByNameTests(TagRepoTestHelper):
    def setUp(self):
        self._clean_tags()

        self.tag_id = "0ebabd4b-d3d1-434b-bfa5-2e1e68492f5d"
        self.tag = "test-tag"
        self.added = "2023-04-16 09:10:25"
        self.updated = "2023-04-16 09:10:25"

        self.subject = TagsRepo()

    def test_get_by_name(self):
        self._seed_db_tag()

        expected_tag = get_tag(self.tag_id, self.tag, self.added, self.updated)

        actual = self.subject.get_by_name(self.tag)

        self._assert_tag(expected_tag, actual)

    def test_get_by_name_notfound_returns_none(self):
        self.assertIsNone(self.subject.get_by_name("unexistent-tag"))

    def _seed_db_tag(self):
        sql = f"""
            INSERT INTO tags (
                id, tag, added, updated
            )
            VALUES (
                '{self.tag_id}',
                '{self.tag}',
                '{self.added}',
                '{self.updated}'
            )
        """
        self._execute_sql(sql)


class GetAllTests(TagRepoTestHelper):
    def setUp(self):
        self._clean_tags()

        self.id_1 = "0ebabd4b-d3d1-434b-bfa5-2e1e68492f5d"
        self.id_2 = "8a388ddc-2bd0-4367-9e91-0e6de2aa8924"
        self.tag_1 = "test-tag_1"
        self.tag_2 = "test-tag_2"
        self.added_1 = "2023-04-16 09:10:25"
        self.added_2 = "2023-04-17 09:10:25"
        self.updated_1 = "2023-04-16 09:10:25"
        self.updated_2 = "2023-04-17 09:10:25"

        self.subject = TagsRepo()

    def test_get_all(self):
        self._seed_db_tags()

        actual = self.subject.get_all()

        expected = [
            get_tag(self.id_1, self.tag_1, self.added_1, self.updated_1),
            get_tag(self.id_2, self.tag_2, self.added_2, self.updated_2),
        ]

        self.assertEqual(len(actual), len(expected))

        for exp, act in zip(expected, actual):
            self._assert_tag(exp, act)

    def _seed_db_tags(self):
        sql = f"""
            INSERT INTO tags (
                id, tag, added, updated
            )
            VALUES (
                '{self.id_1}',
                '{self.tag_1}',
                '{self.added_1}',
                '{self.updated_1}'
            ),
            (
                '{self.id_2}',
                '{self.tag_2}',
                '{self.added_2}',
                '{self.updated_2}'
            )
        """
        self._execute_sql(sql)

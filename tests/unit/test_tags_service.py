from unittest import TestCase
from unittest.mock import patch

from tests.unit.fixtures import get_tag
from services.tags_service import TagsService


class GetTagNamesTests(TestCase):
    def setUp(self):
        repo_patcher = patch("services.tags_service.TagsRepo")
        mock_repo = repo_patcher.start()
        self.mock_get_all = mock_repo.return_value.get_all
        self.addCleanup(repo_patcher.stop)

        self.subject = TagsService()

    def test_success(self):
        tag_1 = "tag_1"
        tag_2 = "tag_2"

        self.mock_get_all.return_value = [
            get_tag("id_1", tag_1),
            get_tag("id_2", tag_2),
        ]

        actual = self.subject.get_tag_names()

        self.assertEqual([tag_1, tag_2], actual)

from typing import List
from repository.tags_repo import TagsRepo


class TagsService:
    def __init__(self):
        self.repo = TagsRepo()

    def get_tag_names(self) -> List[str]:
        return [tag.tag for tag in self.repo.get_all()]

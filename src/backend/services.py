from ..consts import consts
from ..proto.backend_pb2 import GetSupportLinksResponse
from ..proto.generic_pb2 import Empty
from ..proto.services import BackendServiceBase


class BackendService(BackendServiceBase):
    @classmethod
    def get_support_links(cls, request: Empty) -> GetSupportLinksResponse:
        github_page = consts.homepage
        forums_page = consts.support_channels["forums"]
        docs_page = consts.docs_page
        return GetSupportLinksResponse(github_page=github_page, forums_page=forums_page, docs_page=docs_page)

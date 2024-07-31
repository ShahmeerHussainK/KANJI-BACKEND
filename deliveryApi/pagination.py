# from rest_framework.pagination import (LimitOffsetPagination, PageNumberPagination,)
#
# class PostLimitOffsetPagination(LimitOffsetPagination):
#     default_limit = 2
#     max_limit = 10
#
# class PostPageNumberPagination(PageNumberPagination):
#     page_size = 2
#
# # class CustomPagination(pagination.PageNumberPagination):
# #     def get_paginated_response(self, data):
# #         links=({
# #             'links': {
# #                 'next': self.get_next_link(),
# #                 'previous': self.get_previous_link()
# #             },
# #             'count': self.page.paginator.count,
# #             'results': data
# #         })
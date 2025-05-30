from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class AppPagination(PageNumberPagination):
    """
        Pagination Class for deliveries endpoint
    """
    page_size = 50
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        return Response({
            'count': len(data),
            'page': self.page.number,
            'pages_count': self.page.paginator.num_pages,
            'per_page': self.get_page_size(self.request),
            'results': data,
        })

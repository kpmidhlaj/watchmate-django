from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination


class WatchListPagination(PageNumberPagination):
    page_size = 3
    # page_query_param = 'p'
    page_size_query_param = 'size'
    max_page_size = 10
    # last_page_strings = 'end'


class LOPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 10
    offset_query_param = 'skip'



class WatchListCPagination(CursorPagination):
    page_size = 3
    ordering = 'title'
    cursor_query_param = 'orderBy'
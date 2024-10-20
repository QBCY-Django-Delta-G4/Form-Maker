from rest_framework.pagination import CursorPagination


class IdBasedCursorPagination(CursorPagination):
    ordering = 'id'


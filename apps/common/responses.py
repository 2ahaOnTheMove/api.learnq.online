from rest_framework.response import Response
from rest_framework import status as http_status


class APIResponse:
    """
    Standardized API response utility class.
    Use this for consistent success responses.
    """

    @staticmethod
    def success(data=None, message="Success", status=http_status.HTTP_200_OK):
        """Standard success response"""
        return Response(
            {"success": True, "message": message, "data": data}, status=status
        )

    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """201 Created response"""
        return Response(
            {"success": True, "message": message, "data": data},
            status=http_status.HTTP_201_CREATED,
        )

    @staticmethod
    def accepted(data=None, message="Request accepted"):
        """202 Accepted response"""
        return Response(
            {"success": True, "message": message, "data": data},
            status=http_status.HTTP_202_ACCEPTED,
        )

    @staticmethod
    def no_content():
        """204 No Content response"""
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    @staticmethod
    def paginated(data, paginator, request, message="Success"):
        """Paginated response"""
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "page_size": paginator.page.paginator.per_page,
                    "current_page": paginator.page.number,
                    "total_pages": paginator.page.paginator.num_pages,
                },
            },
            status=http_status.HTTP_200_OK,
        )

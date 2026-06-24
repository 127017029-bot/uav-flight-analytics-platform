"""
Reusable pagination classes for the UAV Digital Twin Platform.

Provides three tiers of page sizes tailored to different data volumes:
standard UI lists, large admin exports, and high-frequency telemetry feeds.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Default pagination for most list endpoints (20 items per page)."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """Pagination for bulk / export endpoints (100 items per page)."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class TelemetryPagination(PageNumberPagination):
    """
    High-throughput pagination for telemetry data endpoints.

    Telemetry records are small and requested in bulk for charting and
    analysis, so a larger default page size is appropriate.
    """

    page_size = 500
    page_size_query_param = "page_size"
    max_page_size = 2000

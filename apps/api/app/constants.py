"""
Application-wide constants.

This module defines constants used across the application to avoid hardcoded strings
and reduce the risk of typos.
"""


class AssessmentStatus:
    """
    Assessment status constants.

    These match the database constraint:
    "status IN ('pending', 'processing', 'completed', 'failed')"

    See: app/models/models.py Assessment.status
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    # List of all valid statuses for validation
    ALL = [PENDING, PROCESSING, COMPLETED, FAILED]

    # Active statuses (in progress or completed)
    ACTIVE = [PROCESSING, COMPLETED]

import uuid as uuid_pkg
from datetime import datetime
from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import field_validator

from app.knowledge.models import Document

class DocumentFilter(Filter):
    id: int | None = None
    title: Optional[str] = None
    category: Optional[str] = None

    order_by: Optional[list[str]] = ["-created_at"]

    class Constants(Filter.Constants):
        model = Document

    @field_validator("order_by")
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None

        allowed_field_names = ["created_at",]

        for field_name in value:
            field_name = field_name.replace("+", "").replace("-", "")  #
            if field_name not in allowed_field_names:
                raise ValueError(f"You may only sort by: {', '.join(allowed_field_names)}")

        return value
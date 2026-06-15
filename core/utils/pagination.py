import math
from typing import List, TypeVar, Tuple, Dict, Any
from sqlalchemy import func, select

T = TypeVar("T")

async def paginate(
    session,
    statement: Any,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:

    page = max(1, page)
    offset = (page - 1) * page_size

    count_stmt = select(func.count()).select_from(
        statement.order_by(None).subquery()
    )

    total_count = await session.scalar(count_stmt)

    result = await session.execute(
        statement.offset(offset).limit(page_size)
    )

    items = result.scalars().all()

    pages = math.ceil(total_count / page_size) if total_count else 0

    return {
        "total": total_count,
        "page": page,
        "size": page_size,
        "pages": pages,
        "items": items,
    }
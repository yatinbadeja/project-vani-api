from enum import Enum
from typing import Any, Generic, List, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, model_validator, validator

T = TypeVar("T")

ID = Union[str, int, UUID]


class SortingOrder(str, Enum):
    ASC: int = 1
    DESC: int = -1


class Sort(BaseModel):
    sort_field: str
    sort_order: SortingOrder


class Page(BaseModel):
    page: int = 1
    limit: int = 10

    @validator("page", "limit", pre=True, always=True)
    def default_values(cls, value):
        return value

    @validator("page", "limit", pre=True)
    def validate_positive_values(cls, value):
        if value < 1:
            raise ValueError("Values for page and limit must be positive integers")
        return value

    @validator("page", "limit", pre=True)
    def validate_limit(cls, value):
        if value > 100:
            raise ValueError("Limit cannot exceed 100")
        return value

    @validator("page", "limit", pre=True)
    def validate_page(cls, value):
        if value < 1:
            raise ValueError("Page must be greater than 0")
        return value

    @validator("limit", pre=True)
    def validate_max_limit(cls, value):
        if value < 1:
            raise ValueError("Limit must be greater than 0")
        return value


class PageRequest(BaseModel):
    paging: Page
    sorting: Sort = None


class Meta(Page):
    total: int


class PaginatedResponse(BaseModel):
    docs: List[Any]
    meta: Meta


class AsyncCrudRepository(Generic[T]):
    async def findOne(filter: dict, projection: dict) -> T: ...

    async def findOneById(id: ID) -> T: ...

    async def findAll(filter: dict, projection: dict) -> List[T]: ...

    async def findAllById(ids: List[ID]) -> List[T]: ...

    async def exists(entity: T) -> bool: ...

    async def existsById(id: ID) -> bool: ...

    async def count(filter: Union[dict, None]) -> int: ...

    async def delete(self, entity: T) -> bool: ...

    async def deleteById(self, id: ID) -> bool: ...

    async def deleteAll(self, entities: List[T]) -> bool: ...

    async def deleteAllById(ids: List[ID]) -> bool: ...

    async def save(self, entity: T) -> T: ...

    async def replace(self, entity: T) -> T: ...


class AsyncPagingAndSortingRepository(AsyncCrudRepository[T]):
    async def findAll(
        self, filter: dict, pagination: PageRequest, projection: dict
    ) -> PaginatedResponse: ...

    async def findAllById(ids: List[ID], pagingation: PageRequest) -> List[T]: ...

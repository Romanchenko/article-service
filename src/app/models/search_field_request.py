from typing_extensions import TypedDict


class SearchFieldRequest(TypedDict):
    field: str
    value: str
    full_match: bool

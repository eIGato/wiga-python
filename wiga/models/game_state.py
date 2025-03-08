__all__ = [
    "GameState",
    "GameStateDiff",
    "State",
    "StateDiff",
]

import typing as ty
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

StateType = ty.TypeVar("StateType", bound="State")


class StateDiff:
    def __init__(
        self,
        **kwargs,
    ):
        vars(self).update(**kwargs)


@dataclass(slots=True, kw_only=True)
class State:
    ignore: ty.Collection[str] = ()

    def __sub__(self: StateType, other: StateType) -> StateDiff:
        return StateDiff(**self.get_diff(other))

    def get_diff(self: StateType, other: StateType) -> dict:
        diff = {}
        ignore = self.ignore
        for attr in self.__slots__:
            if attr in ignore:
                continue
            left = getattr(other, attr)
            right = getattr(self, attr)
            sub_result = get_diff(left, right)
            if sub_result is not None:
                diff[attr] = sub_result
        return diff


class GameStateDiff(StateDiff):
    left_id: int
    right_id: int

    def __init__(self, left_id: int, right_id: int, **kwargs):
        assert "left_id" not in kwargs
        assert "right_id" not in kwargs
        super().__init__(**kwargs)
        vars(self).update(left_id=left_id, right_id=right_id)


@dataclass(slots=True, kw_only=True)
class GameState(State, ABC):
    id: int = 0
    ignore: ty.Collection[str] = ("id",)

    def __sub__(self: StateType, other: StateType) -> GameStateDiff:
        return GameStateDiff(
            left_id=other.id,
            right_id=self.id,
            **self.get_diff(other),
        )

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_perspective(self, seen_by):
        pass


def get_diff(left, right):
    assert type(left) is type(right)
    if isinstance(left, State):
        sub_result = right - left
        if len(vars(sub_result)) > 2 * len(left.ignore):
            return sub_result
    elif isinstance(left, list):
        sub_result = right[right.index(left[-1]) :]
        if sub_result:
            return sub_result
    elif isinstance(left, dict):
        sub_result = {}
        for key, value in left.items():
            value_diff = get_diff(value, right[key])
            if value_diff is not None:
                sub_result[key] = value_diff
        if sub_result:
            return sub_result
    else:
        if left != right:
            return right

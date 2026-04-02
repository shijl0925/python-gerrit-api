#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GerritBase:
    """
    This appears to be the base object that all other gerrit objects are
    inherited from
    """

    def __init__(self, pull: bool = True) -> None:
        """
        Initialize and populate this resource object from the Gerrit API.
        """
        self._data: Any = None
        if pull:
            self.poll()

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__} {str(self)}>"

    def __str__(self) -> str:
        raise NotImplementedError

    def poll(self) -> None:
        data = self._poll()
        self._data = data

        if isinstance(self._data, dict):
            for key, value in self._data.items():
                try:
                    if key and key[0] == "_":
                        key = key[1:]
                    setattr(self, key, value)
                except AttributeError:
                    logger.debug("Skipping read-only attribute %r", key)

    def _poll(self) -> Any:
        res = self.gerrit.get(self.endpoint)  # pylint: disable=no-member

        if isinstance(res, list) and res:
            return res[0]

        return res

    def to_dict(self) -> Any:
        """
        Print out all the data in this object for debugging.
        """
        return self._data

    def __eq__(self, other: object) -> bool:
        """
        Return true if the other object represents a connection to the
        same server
        """
        if not isinstance(other, self.__class__):
            return False
        return other.endpoint == self.endpoint  # pylint: disable=no-member

    def __hash__(self) -> int:
        return hash(self.endpoint)  # pylint: disable=no-member

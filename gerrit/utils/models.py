#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from copy import deepcopy


class ResultSet(list):
    """A list like object that holds results from a Gerrit API query."""


class BaseModel(object):
    def __init__(self, **kwargs):
        self.entity_name = "id"
        self.content = None

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__.get(key)
        else:
            raise AttributeError(key)

    @classmethod
    def parse(cls, data, **kwargs):
        """Parse a JSON object into a model instance."""
        data = data or {}

        item = cls() if data else None

        content = deepcopy(data)
        setattr(item, "content", content)

        data.update(kwargs)

        for key, value in data.items():
            try:
                if key[0] == '_':
                    key = key[1:]
                setattr(item, key, value)
            except AttributeError:
                pass

        return item

    @classmethod
    def parse_list(cls, data, **kwargs):
        """Parse a list of JSON objects into a result set of model instances."""
        results = ResultSet()
        data = data or []
        for obj in data:
            if obj:
                results.append(cls.parse(obj, **kwargs))
        return results

    @classmethod
    def parse_dict(cls, data, **kwargs):
        """Parse a dict of JSON objects into a result set of model instances."""
        results = ResultSet()
        data = data or {}
        for obj in data.keys():
            if obj:
                results.append(cls.parse(data[obj], **kwargs))
        return results

    def __repr__(self):
        key = self.entity_name
        value = getattr(self, key)
        return "%s(%s=%s)" % (self.__class__.__name__, key, value)

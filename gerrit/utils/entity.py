#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import json
from gerrit.utils.common import logger


class Entity(object):
    required = ()
    optional = ()

    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        self.attributes = self.required + self.optional

        for item in self.required:
            if item not in kwargs.keys():
                name = self.__class__.__name__
                logger.warning(
                    f"*** Warning! {name} missing a required keyword argument '{item}' ***"
                )

        for (k, v) in kwargs.items():
            if k in self.attributes:
                setattr(self, k, v)
            else:
                name = self.__class__.__name__
                logger.warning(
                    f"*** Warning! {name} got an unexpected keyword argument: '{k}' ***"
                )

    def __getattr__(self, key):
        return self.__dict__.get(key, None)

    def __str__(self):
        """

        :return:
        """
        review_input = {}
        for key in self.attributes:
            value = getattr(self, key)
            if value:
                review_input.update({key: value})

        return json.dumps(review_input, sort_keys=True)

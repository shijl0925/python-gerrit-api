#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class Task(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = "/config/server/tasks"

    def delete(self):
        """
        Kills a task from the background work queue that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{self.id}")


class Tasks(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit
        self.endpoint = "/config/server/tasks"

    def list(self):
        """
        Lists the tasks from the background work queues that the Gerrit daemon is currently
        performing, or will perform in the near future.

        :return:
        """
        result = self.gerrit.get(self.endpoint)
        return Task.parse_list(result, gerrit=self.gerrit)

    def get(self, id_):
        """
        Retrieves a task from the background work queue that the Gerrit daemon is currently
        performing, or will perform in the near future.

        :param id_: task id
        :return:
        """

        result = self.gerrit.get(self.endpoint + f"/{id_}")
        return Task(json=result, gerrit=self.gerrit)

    def delete(self, id_):
        """
        Kills a task from the background work queue that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :param id_: task id
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{id_}")

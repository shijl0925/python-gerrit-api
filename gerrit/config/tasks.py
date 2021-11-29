#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class Task(BaseModel):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)

    def delete(self):
        """
        Kills a task from the background work queue that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :return:
        """
        endpoint = "/config/server/tasks/%s" % self.id
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class Tasks(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def list(self):
        """
        Lists the tasks from the background work queues that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :return:
        """
        endpoint = "/config/server/tasks/"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return Task.parse_list(result, gerrit=self.gerrit)

    def get(self, id_):
        """
        Retrieves a task from the background work queue that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :param id_: task id
        :return:
        """
        endpoint = "/config/server/tasks/%s" % id_
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return Task.parse(result, gerrit=self.gerrit)

    def delete(self, id_):
        """
        Kills a task from the background work queue that the Gerrit daemon is currently performing,
        or will perform in the near future.

        :param id_: task id
        :return:
        """
        endpoint = "/config/server/tasks/%s" % id_
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

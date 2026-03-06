#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.config and gerrit.plugins — all HTTP calls are mocked.
"""
import logging
import pytest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GerritConfig
# ---------------------------------------------------------------------------

class TestGerritConfig:

    def test_get_version(self, mock_gerrit):
        mock_gerrit.get.return_value = "3.7.1"
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_version()
        assert result == "3.7.1"

    def test_get_server_info(self, mock_gerrit):
        mock_gerrit.get.return_value = {"gerrit": {"all_projects": "All-Projects"}}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_server_info()
        assert "gerrit" in result

    def test_check_consistency(self, mock_gerrit):
        mock_gerrit.post.return_value = {"check_accounts": {"problems": []}}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.check_consistency({"check_accounts": {}})
        mock_gerrit.post.assert_called()

    def test_reload_config(self, mock_gerrit):
        mock_gerrit.post.return_value = {}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.reload_config()
        mock_gerrit.post.assert_called()

    def test_confirm_email(self, mock_gerrit):
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.confirm_email({"token": "abc123"})
        mock_gerrit.put.assert_called()

    def test_get_summary(self, mock_gerrit):
        mock_gerrit.get.return_value = {"task_summary": {}, "mem_summary": {}}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_summary()
        assert isinstance(result, dict)

    def test_get_summary_with_option(self, mock_gerrit):
        mock_gerrit.get.return_value = {"jvm": {}}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_summary(option="jvm")
        assert isinstance(result, dict)

    def test_list_capabilities(self, mock_gerrit):
        mock_gerrit.get.return_value = {"administrateServer": {}}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.list_capabilities()
        assert isinstance(result, dict)

    def test_get_top_menus(self, mock_gerrit):
        mock_gerrit.get.return_value = []
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_top_menus()
        assert isinstance(result, list)

    def test_get_default_user_preferences(self, mock_gerrit):
        mock_gerrit.get.return_value = {"changes_per_page": 25}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_default_user_preferences()
        assert "changes_per_page" in result

    def test_set_default_user_preferences(self, mock_gerrit):
        mock_gerrit.put.return_value = {"changes_per_page": 50}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.set_default_user_preferences({"changes_per_page": 50})
        mock_gerrit.put.assert_called()

    def test_get_default_diff_preferences(self, mock_gerrit):
        mock_gerrit.get.return_value = {"line_length": 100}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_default_diff_preferences()
        assert "line_length" in result

    def test_set_default_diff_preferences(self, mock_gerrit):
        mock_gerrit.put.return_value = {"line_length": 120}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.set_default_diff_preferences({"line_length": 120})
        mock_gerrit.put.assert_called()

    def test_get_default_edit_preferences(self, mock_gerrit):
        mock_gerrit.get.return_value = {"line_length": 80}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        result = config.get_default_edit_preferences()
        assert "line_length" in result

    def test_set_default_edit_preferences(self, mock_gerrit):
        mock_gerrit.put.return_value = {"tab_size": 4}
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.set_default_edit_preferences({"tab_size": 4})
        mock_gerrit.put.assert_called()

    def test_index_changes(self, mock_gerrit):
        from gerrit.config.config import GerritConfig
        config = GerritConfig(gerrit=mock_gerrit)
        config.index_changes({"changes": ["foo~101"]})
        mock_gerrit.post.assert_called()

    def test_caches_property(self, mock_gerrit):
        from gerrit.config.config import GerritConfig
        from gerrit.config.caches import Caches
        config = GerritConfig(gerrit=mock_gerrit)
        assert isinstance(config.caches, Caches)

    def test_tasks_property(self, mock_gerrit):
        from gerrit.config.config import GerritConfig
        from gerrit.config.tasks import Tasks
        config = GerritConfig(gerrit=mock_gerrit)
        assert isinstance(config.tasks, Tasks)


# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

class TestCaches:

    def test_list_caches(self, mock_gerrit):
        mock_gerrit.get.return_value = {
            "accounts": {"name": "accounts", "entries": {"mem": 5}, "average_get": "0.01ms"},
            "groups": {"name": "groups", "entries": {"mem": 2}, "average_get": "0.02ms"},
        }
        from gerrit.config.caches import Caches
        caches = Caches(gerrit=mock_gerrit)
        result = caches.list()
        assert len(result) == 2

    def test_get_cache(self, mock_gerrit):
        mock_gerrit.get.return_value = {"name": "accounts", "entries": {"mem": 5}}
        from gerrit.config.caches import Caches, Cache
        caches = Caches(gerrit=mock_gerrit)
        cache = caches.get("accounts")
        assert isinstance(cache, Cache)

    def test_flush_cache_by_name(self, mock_gerrit):
        from gerrit.config.caches import Caches
        caches = Caches(gerrit=mock_gerrit)
        caches.flush("accounts")
        mock_gerrit.post.assert_called()

    def test_cache_operation(self, mock_gerrit):
        from gerrit.config.caches import Caches
        caches = Caches(gerrit=mock_gerrit)
        caches.operation({"operation": "FLUSH_ALL"})
        mock_gerrit.post.assert_called()

    def test_cache_flush(self, mock_gerrit):
        mock_gerrit.get.return_value = {"name": "accounts", "entries": {"mem": 5}}
        from gerrit.config.caches import Caches
        caches = Caches(gerrit=mock_gerrit)
        cache = caches.get("accounts")
        cache.flush()
        mock_gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TestTasks:

    def test_list_tasks(self, mock_gerrit):
        mock_gerrit.get.return_value = [{"id": "task1", "state": "SLEEPING"}]
        from gerrit.config.tasks import Tasks
        tasks = Tasks(gerrit=mock_gerrit)
        result = tasks.list()
        assert len(result) >= 1

    def test_get_task(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "task1", "state": "SLEEPING", "delay": 1000}
        from gerrit.config.tasks import Tasks, Task
        tasks = Tasks(gerrit=mock_gerrit)
        task = tasks.get("task1")
        assert isinstance(task, Task)

    def test_delete_task(self, mock_gerrit):
        from gerrit.config.tasks import Tasks
        tasks = Tasks(gerrit=mock_gerrit)
        tasks.delete("task1")
        mock_gerrit.delete.assert_called()

    def test_task_delete(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "task1", "state": "SLEEPING"}
        from gerrit.config.tasks import Tasks
        tasks = Tasks(gerrit=mock_gerrit)
        task = tasks.get("task1")
        task.delete()
        mock_gerrit.delete.assert_called()


# ---------------------------------------------------------------------------
# GerritPlugins
# ---------------------------------------------------------------------------

class TestGerritPlugins:

    def test_list_plugins(self, mock_gerrit):
        mock_gerrit.get.return_value = {
            "delete-project": {"id": "delete-project", "version": "2.0"},
            "replication": {"id": "replication", "version": "3.0"},
        }
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        result = plugins.list()
        assert isinstance(result, dict)

    def test_list_plugins_is_all(self, mock_gerrit):
        mock_gerrit.get.return_value = {"delete-project": {"id": "delete-project"}}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        result = plugins.list(is_all=True)
        assert isinstance(result, dict)

    def test_list_plugins_with_pattern(self, mock_gerrit):
        mock_gerrit.get.return_value = {"delete-project": {"id": "delete-project"}}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        result = plugins.list(pattern_dispatcher={"prefix": "delete"})
        assert isinstance(result, dict)

    def test_get_plugin(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "delete-project", "version": "2.0", "disabled": False}
        from gerrit.plugins.plugins import GerritPlugins, GerritPlugin
        plugins = GerritPlugins(gerrit=mock_gerrit)
        plugin = plugins.get("delete-project")
        assert isinstance(plugin, GerritPlugin)

    def test_install_plugin(self, mock_gerrit):
        mock_gerrit.put.return_value = {"id": "new-plugin", "version": "1.0"}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        result = plugins.install("new-plugin", {"url": "file:///gerrit/plugins/new-plugin.jar"})
        mock_gerrit.put.assert_called()

    def test_plugin_enable(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "delete-project"}
        mock_gerrit.post.return_value = {"id": "delete-project", "disabled": False}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        plugin = plugins.get("delete-project")
        plugin.enable()
        mock_gerrit.post.assert_called()

    def test_plugin_disable(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "delete-project"}
        mock_gerrit.post.return_value = {"id": "delete-project", "disabled": True}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        plugin = plugins.get("delete-project")
        plugin.disable()
        mock_gerrit.post.assert_called()

    def test_plugin_reload(self, mock_gerrit):
        mock_gerrit.get.return_value = {"id": "delete-project"}
        mock_gerrit.post.return_value = {"id": "delete-project"}
        from gerrit.plugins.plugins import GerritPlugins
        plugins = GerritPlugins(gerrit=mock_gerrit)
        plugin = plugins.get("delete-project")
        plugin.reload()
        mock_gerrit.post.assert_called()

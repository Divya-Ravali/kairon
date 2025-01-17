import os
from unittest.mock import patch

import pytest
import responses
from bson import ObjectId
from mongoengine import connect, ValidationError

from kairon.exceptions import AppException
from kairon.shared.chat.notifications.processor import MessageBroadcastProcessor
from kairon.shared.utils import Utility


class TestMessageBroadcastProcessor:

    @pytest.fixture(autouse=True, scope='class')
    def setup(self):
        os.environ["system_file"] = "./tests/testing_data/system.yaml"
        Utility.load_environment()
        Utility.load_system_metadata()
        db_url = Utility.environment['database']["url"]
        pytest.db_url = db_url
        connect(**Utility.mongoengine_connection(Utility.environment['database']["url"]))
        responses.reset()

    def test_add_scheduler_task_channel_not_configured(self):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "first_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "57 22 * * *"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        with pytest.raises(AppException, match=f"Channel 'whatsapp' not configured!"):
            MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

    @patch("kairon.shared.utils.Utility.is_exist", autospec=True)
    def test_add_scheduled_task(self, mock_channel_config):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "first_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "57 22 * * *",
                "timezone": "Asia/Kolkata"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        assert MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

    def test_add_scheduler_exists(self):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "first_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "57 22 * * *"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        with pytest.raises(AppException, match=f"Schedule with name '{config['name']}' exists!"):
            MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

    @patch("kairon.shared.utils.Utility.is_exist", autospec=True)
    def test_add_scheduler_one_time_trigger(self, mock_channel_config):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "second_scheduler",
            "connector_type": "slack",
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "data_extraction_config": {
                "url": "https://demo.url",
                "headers": {
                    "authorization": "bearer token",
                    "request": "from app"
                }
            },
            "template_config": [
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        assert MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

    @patch("kairon.shared.utils.Utility.is_exist", autospec=True)
    def test_add_scheduled_task_invalid_schedule(self, mock_channel_config):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "third_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "* * * * *"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        with pytest.raises(ValidationError, match=f"recurrence interval must be at least 86340 seconds!"):
            MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

        config["scheduler_config"]["schedule"] = ""
        with pytest.raises(ValidationError, match="Invalid cron expression: ''"):
            MessageBroadcastProcessor.add_scheduled_task(bot, user, config)

    @patch("kairon.shared.utils.Utility.is_exist", autospec=True)
    def test_update_scheduled_task(self, mock_channel_config):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "first_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "30 22 5 * *",
                "timezone": "Asia/Kolkata"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "dynamic",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                    "data": ""
                },
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        first_scheduler_config = list(MessageBroadcastProcessor.list_settings(bot, name="first_scheduler"))[0]
        assert first_scheduler_config

        MessageBroadcastProcessor.update_scheduled_task(first_scheduler_config["_id"], bot, user, config)

    def test_updated_scheduled_task_not_exists(self):
        bot = "test_achedule"
        user = "test_user"
        config = {
            "name": "first_scheduler",
            "connector_type": "whatsapp",
            "scheduler_config": {
                "expression_type": "cron",
                "schedule": "30 22 5 * *"
            },
            "recipients_config": {
                "recipient_type": "static",
                "recipients": "918958030541, "
            },
            "template_config": [
                {
                    "template_type": "dynamic",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                    "data": ""
                },
                {
                    "template_type": "static",
                    "template_id": "brochure_pdf",
                    "namespace": "13b1e228_4a08_4d19_a0da_cdb80bc76380",
                }
            ]
        }
        with pytest.raises(AppException, match="Notification settings not found!"):
            MessageBroadcastProcessor.update_scheduled_task(ObjectId().__str__(), bot, user, config)

    def test_update_schedule_invalid_scheduler(self):
        bot = "test_achedule"
        user = "test_user"
        first_scheduler_config = list(MessageBroadcastProcessor.list_settings(bot, name="first_scheduler"))[0]
        assert first_scheduler_config
        first_scheduler_config["scheduler_config"] = None
        with pytest.raises(AppException, match="scheduler_config is required!"):
            MessageBroadcastProcessor.update_scheduled_task(first_scheduler_config["_id"], bot, user, first_scheduler_config)

    def test_get_settings(self):
        bot = "test_achedule"
        settings = list(MessageBroadcastProcessor.list_settings(bot))
        config_id = settings[0].pop("_id")
        assert isinstance(config_id, str)
        config_id = settings[1].pop("_id")
        assert isinstance(config_id, str)
        settings[0].pop("timestamp")
        settings[1].pop("timestamp")
        assert settings == [{'name': 'first_scheduler', 'connector_type': 'whatsapp',
                             'scheduler_config': {'expression_type': 'cron', 'schedule': '30 22 5 * *',
                                                  "timezone": "Asia/Kolkata"},
                             'recipients_config': {'recipient_type': 'static', 'recipients': '918958030541,'},
                             'template_config': [{'template_type': 'dynamic', 'template_id': 'brochure_pdf',
                                                  'language': "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380', 'data': ''},
                                                 {'template_type': 'static', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380'}],
                             'bot': 'test_achedule', 'user': 'test_user', 'status': True},
                            {'name': 'second_scheduler', 'connector_type': 'slack',
                             'data_extraction_config': {'method': 'GET', 'url': 'https://demo.url',
                                                        'headers': {'authorization': 'bearer token',
                                                                    'request': 'from app'}, 'request_body': {}},
                             'recipients_config': {'recipient_type': 'static', 'recipients': '918958030541,'},
                             'template_config': [{'template_type': 'static', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380'}],
                             'bot': 'test_achedule', 'user': 'test_user', 'status': True}]

        setting = MessageBroadcastProcessor.get_settings(config_id, bot)
        assert isinstance(setting.pop("_id"), str)
        setting.pop("timestamp")
        assert setting == {'name': 'second_scheduler', 'connector_type': 'slack',
                             'data_extraction_config': {'method': 'GET', 'url': 'https://demo.url',
                                                        'headers': {'authorization': 'bearer token',
                                                                    'request': 'from app'}, 'request_body': {}},
                             'recipients_config': {'recipient_type': 'static', 'recipients': '918958030541,'},
                             'template_config': [{'template_type': 'static', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380'}],
                             'bot': 'test_achedule', 'user': 'test_user', 'status': True}

    def test_get_settings_not_found(self):
        bot = "test_schedule"
        assert [] == list(MessageBroadcastProcessor.list_settings(bot, name="first_scheduler"))

        with pytest.raises(AppException, match="Notification settings not found!"):
            MessageBroadcastProcessor.get_settings(ObjectId().__str__(), bot)

    def test_delete_schedule(self):
        bot = "test_achedule"
        first_scheduler_config = list(MessageBroadcastProcessor.list_settings(bot, name="first_scheduler"))[0]
        MessageBroadcastProcessor.delete_task(first_scheduler_config["_id"], bot, False)

        settings = list(MessageBroadcastProcessor.list_settings(bot, status=True))
        config_id = settings[0].pop("_id")
        assert isinstance(config_id, str)
        settings[0].pop("timestamp")
        assert settings == [{'name': 'second_scheduler', 'connector_type': 'slack',
                             'data_extraction_config': {'method': 'GET', 'url': 'https://demo.url',
                                                        'headers': {'authorization': 'bearer token',
                                                                    'request': 'from app'}, 'request_body': {}},
                             'recipients_config': {'recipient_type': 'static', 'recipients': '918958030541,'},
                             'template_config': [{'template_type': 'static', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380'}],
                             'bot': 'test_achedule', 'user': 'test_user', 'status': True}]

        settings = list(MessageBroadcastProcessor.list_settings(bot, status=False))
        config_id = settings[0].pop("_id")
        assert isinstance(config_id, str)
        settings[0].pop("timestamp")
        assert settings == [{'name': 'first_scheduler', 'connector_type': 'whatsapp',
                             'scheduler_config': {'expression_type': 'cron', 'schedule': '30 22 5 * *', "timezone": "Asia/Kolkata"},
                             'recipients_config': {'recipient_type': 'static', 'recipients': '918958030541,'},
                             'template_config': [{'template_type': 'dynamic', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380', 'data': ''},
                                                 {'template_type': 'static', 'template_id': 'brochure_pdf',
                                                  "language": "en",
                                                  'namespace': '13b1e228_4a08_4d19_a0da_cdb80bc76380'}],
                             'bot': 'test_achedule', 'user': 'test_user', 'status': False}]

    def test_delete_schedule_not_exists(self):
        bot = "test_achedule"
        with pytest.raises(AppException, match="Notification settings not found!"):
            MessageBroadcastProcessor.delete_task(ObjectId().__str__(), bot)

        with pytest.raises(AppException, match="Notification settings not found!"):
            MessageBroadcastProcessor.delete_task(ObjectId().__str__(), bot, True)

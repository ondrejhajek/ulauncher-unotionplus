import json
import re
import requests
import os
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
import utils
from datetime import datetime

class UNotion:
    RESULTS_ALREADY_SEARCHED = []
    NOTION_API_URL = "https://api.notion.com/v1"
    EXTENSION_PREFERENCES = []
    NOTIFICATION_ICON = os.getcwd() + "/images/icon.png"

    def __init__(self, extension_preferences):
        self.EXTENSION_PREFERENCES = extension_preferences
        Notify.init("UNotion")

    def get_databases_linked(self):
        if not self.RESULTS_ALREADY_SEARCHED or len(self.RESULTS_ALREADY_SEARCHED) == 0:
            response = self.make_request_to_api('/search', {})
            self.RESULTS_ALREADY_SEARCHED = response.json()['results']

        return self.RESULTS_ALREADY_SEARCHED

    def upload_to_notion(self, database_id, note):

        tags_pattern = r'#(\w+)'
        tags = re.findall(tags_pattern, note)
        text_without_tags = re.sub(tags_pattern, '', note).strip()

        data = {
            "parent": {"database_id": database_id},
            "properties": {
                self.EXTENSION_PREFERENCES.get('title_property'): {"title": [{"text": {"content": text_without_tags}}]}
            }
        }

        if tags:
            data["properties"][self.EXTENSION_PREFERENCES.get('tags_property')] = self.build_tags(tags)

        api_response = self.make_request_to_api('/pages', data)

        if api_response.status_code == 200:
            Notify.Notification.new("New note was successfully created", "", self.NOTIFICATION_ICON).show()
        else:
            Notify.Notification.new("Error! Note was not created.", "", self.NOTIFICATION_ICON).show()

    def get_items_from_database(self, database_id):

        api_response = self.make_request_to_api('/databases/' + database_id + "/query", {})

        api_items = api_response.json().get('results', [])

        items = []

        for item in api_items:
            title_property = item.get('properties', {}).get(self.EXTENSION_PREFERENCES.get('title_property'), {}).get('title', [{}])[0].get('text', {}).get(
                'content', '')
            tags_property = item.get('properties', {}).get(self.EXTENSION_PREFERENCES.get('tags_property'), {}).get('multi_select', [])
            tags = [tag.get('name') for tag in tags_property]
            url_property = item.get('url')
            items.append({
                'title': utils.sanitize(title_property, 55),
                'url': url_property,
                'created_time': datetime.strptime(item.get('created_time'), "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y"),
                'tags': ' '.join(['#' + tag for tag in tags])
            })
        print(items)
        return items


    def build_tags(self, tags):
        multi_select = []
        for tag in tags:
            multi_select.append({"name": tag})
        return {
            "multi_select": multi_select
        }

    def make_request_to_api(self, uri, data):
        headers = {
            "Authorization": "Bearer %s" % self.EXTENSION_PREFERENCES.get('notion_token'),
            "Content-type": "application/json",
            "Notion-Version": "2021-08-16"
        }
        return requests.post(self.NOTION_API_URL + uri, headers=headers, data=json.dumps(data))

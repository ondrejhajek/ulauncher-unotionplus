from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from UNotion import UNotion


class NotionPlusNotes(Extension):
    UNOTION = None

    def __init__(self):
        super(NotionPlusNotes, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        if not extension.UNOTION:
            extension.UNOTION = UNotion(extension.preferences)

        for database in extension.UNOTION.get_databases_linked():
            if database["object"] == "database":
                db_name = database["title"][0]["text"]["content"]
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name='%s' % db_name,
                                                 description='Browse database or add note to database %s' % db_name,
                                                 on_enter=ExtensionCustomAction({'action': 'list_database_items', 'database_name': db_name, 'database_id': database["id"], 'note': event.get_argument()}, keep_app_open=True)))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        data = event.get_data()

        if data['action'] == 'add_note':

            if data['note'] is not None:
                extension.UNOTION.upload_to_notion(data['database_id'], data['note'])

        if data['action'] == 'list_database_items':

            items_from_database = extension.UNOTION.get_items_from_database(data['database_id'])

            items = []

            if data['note'] is not None:
                items.append(ExtensionResultItem(icon='images/add.png',
                                                 name='Add note',
                                                 description=f'Add entered note to {data["database_name"]}',
                                                 on_enter=ExtensionCustomAction({'action': 'add_note',
                                                                                 'database_id': data['database_id'],
                                                                                 'note': data['note']}, False)))

            i = 0
            for item_from_database in items_from_database:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=item_from_database['title'],
                                                 description=f'Created: {item_from_database.get("created_time")} | tags: {item_from_database.get("tags")}',
                                                 on_enter=OpenUrlAction(item_from_database['url'])))
                i += 1
                if i == 10:
                    break


            return RenderResultListAction(items)




if __name__ == '__main__':
    NotionPlusNotes().run()

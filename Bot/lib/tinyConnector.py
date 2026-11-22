from typing import Union

from tinydb import TinyDB, Query


class TinyConnector:
    _current_file = 'servers.json'
    db = TinyDB(_current_file)
    settings = db.table('guild_settings')
    q = Query()


    @staticmethod
    def delete_guild(guild_id: Union[str, int]) -> int:
        """delete all data for the given guild
           returns the number of deleted entries

           also removes legacy automock entries from the default table

        Args:
            guild_id (Union[str, int]): id of the guild

        Returns:
            int: number of deleted items
        """
        guild_id = str(guild_id)

        result = TinyConnector.db.remove(TinyConnector.q.guild_id == guild_id)
        result += TinyConnector.settings.remove(TinyConnector.q.guild_id == guild_id)
        return len(result)


    @staticmethod
    def get_guild_ids() -> set[int]:
        """get the ids of all guilds with stored data (incl. legacy entries)"""
        entries = TinyConnector.db.all() + TinyConnector.settings.all()
        return {int(e['guild_id']) for e in entries if 'guild_id' in e}


    @staticmethod
    def get_delete_on_mock(guild_id: Union[str, int]) -> bool:
        """whether the original message should be deleted after mocking it
           defaults to True if the guild has no stored setting
        """
        guild_id = str(guild_id)

        db_json = TinyConnector.settings.get(TinyConnector.q.guild_id == guild_id)
        if not db_json:
            return True
        return db_json.get('delete_on_mock', True)


    @staticmethod
    def set_delete_on_mock(guild_id: Union[str, int], enabled: bool):
        guild_id = str(guild_id)

        TinyConnector.settings.upsert({'guild_id': guild_id, 'delete_on_mock': bool(enabled)},
                                      TinyConnector.q.guild_id == guild_id)

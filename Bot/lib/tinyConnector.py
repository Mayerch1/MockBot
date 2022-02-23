from decimal import *
from enum import Enum
from typing import Union

from tinydb import TinyDB, Query


class MockStatus(Enum):
    no_action = 0
    automock = 1
    blacklist = 2


class Server:
    g_id: str = None  # id
    user_list: dict[MockStatus] = {}


class TinyConnector:
    _current_file = 'servers.json'
    db = TinyDB(_current_file)
    q = Query()


    @staticmethod
    def delete_guild(guild_id: Union[str, int]) -> int:
        """delete all data for the given guild
           returns the number of deleted entries/users

        Args:
            guild_id (Union[str, int]): id of the guild

        Returns:
            int: number of deleted items
        """
        guild_id = str(guild_id)

        result = TinyConnector.db.remove(TinyConnector.q.guild_id == guild_id)
        return len(result)

 
    @staticmethod
    def set_member_status(guild_id: Union[str, int], user_id: Union[str, int], new_status: MockStatus):
        guild_id = str(guild_id)
        user_id = str(user_id)
        new_status = new_status.value

        d = {
            'guild_id': guild_id,
            'user_id': user_id,
            'status': new_status
        }
        TinyConnector.db.upsert(d, (TinyConnector.q.guild_id == guild_id) and (TinyConnector.q.user_id == user_id))


    @staticmethod
    def get_member_status(guild_id: Union[str, int], user_id: Union[str, int]) -> MockStatus:
        
        guild_id = str(guild_id)
        user_id = str(user_id)

        db_json = TinyConnector.db.get((TinyConnector.q.guild_id == guild_id) and (TinyConnector.q.user_id == user_id))

        if not db_json:
            return MockStatus.no_action
        else:
            return MockStatus(db_json['status'])


    @staticmethod
    def get_mocked_users(guild_id: Union[str, int]) -> list[int]:

        guild_id = str(guild_id)

        db_json = TinyConnector.db.search((TinyConnector.q.guild_id == guild_id) and (TinyConnector.q.status == MockStatus.automock.value))

        return [int(entry['user_id']) for entry in db_json]
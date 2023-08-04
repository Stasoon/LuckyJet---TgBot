from typing import Generator

from .models import Channel


# region SQL Create

def save_channel(channel_id: str, title: str, url: str) -> None:
    if not is_channel_already_exist(channel_id):
        Channel.create(channel_id=channel_id, title=title, url=url)
    else:
        channel = Channel.get(Channel.channel_id == channel_id)
        channel.update(channel_id=channel_id, title=title, url=url)
        channel.save()

# endregion


# region SQL Read

def is_channel_already_exist(channel_id: str) -> bool:
    return bool(Channel.get_or_none(Channel.channel_id == channel_id))


def get_channels_full_data() -> Generator[dict, None, None]:
    yield from [{'id': channel.channel_id, 'title': channel.title, 'url': channel.url}
                for channel in Channel.select()]


def get_channel_ids() -> tuple:
    channel_ids = [channel.channel_id for channel in Channel.select()]
    return tuple(channel_ids)


# endregion


# region SQL Delete

def delete_channel(channel_id: str) -> None:
    channel = Channel.get(Channel.channel_id == channel_id)
    channel.delete_instance()

# endregion

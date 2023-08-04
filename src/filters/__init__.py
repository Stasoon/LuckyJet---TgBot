from aiogram import Dispatcher

from .is_admin import IsAdminFilter
from .is_sub import IsSubFilter


def register_all_filters(dp: Dispatcher):
    # сюда прописывать фильтры
    filters = (
        IsAdminFilter,
        IsSubFilter,
    )

    for fltr in filters:
        dp.filters_factory.bind(fltr)

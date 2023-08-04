from .models import Admin


def add_admin(telegram_id: int, admin_name: str):
    if is_admin_exist(telegram_id):
        Admin.update(name=admin_name).where(Admin.telegram_id == telegram_id)
    else:
        Admin.create(telegram_id=telegram_id, name=admin_name)


def delete_admin(telegram_id: int) -> bool:
    try:
        Admin.delete().where(Admin.telegram_id == telegram_id).execute()
    except Admin.DoesNotExist:
        return False
    else:
        return True


def get_admins():
    return [(admin.telegram_id, admin.name) for admin in Admin.select()]


def get_admin_ids():
    return [admin.telegram_id for admin in Admin.select()]


def is_admin_exist(telegram_id: int):
    admin = Admin.get_or_none(Admin.telegram_id == telegram_id)
    return True if admin else False


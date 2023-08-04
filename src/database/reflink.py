from .models import ReferralLink, User


def get_link(reflink: str) -> list | None:
    link = ReferralLink.get_or_none(ReferralLink.name == reflink)
    return (link.name, link.user_count, link.passed_op_count) if link else None


def get_link_names() -> list:
    return [link.name for link in ReferralLink.select()]


def increase_or_create_reflink(reflink: str):
    try:
        increase_users_count(reflink)
    except ReferralLink.DoesNotExist:
        create_reflink(reflink)


def create_reflink(reflink: str):
    ReferralLink.create(name=reflink)


def increase_users_count(reflink: str) -> None:
    try:
        link = ReferralLink.get(ReferralLink.name == reflink)
        link.user_count += 1
        link.save()
    except ReferralLink.DoesNotExist:
        pass


def increase_op_count(user_id: int) -> None:
    try:
        link = ReferralLink.get(ReferralLink.name == User.get(User.telegram_id == user_id).referral_link)
        link.passed_op_count += 1
        link.save()
    except (User.DoesNotExist, ReferralLink.DoesNotExist):
        pass


def is_reflink_exists(reflink: str) -> bool:
    return bool(ReferralLink.get_or_none(ReferralLink.name == reflink))


def delete_reflink(reflink: str):
    ReferralLink.delete().where(ReferralLink.name == reflink).execute()



from django.utils import timezone
from django.db.models import Q

from messages_extends.models import Message
from messages_extends import constants


def add_message(user, message, level=constants.INFO_PERSISTENT, tags=None, expires=None):
    """
    Add a message for the specified user.
    """
    now = timezone.now()
    get_kwargs = dict(
        user=user,
        message=message,
        level=level,
        read=False
    )
    if tags:
        get_kwargs['extra_tags'] = tags
    msg = Message.objects.filter(Q(expires=None) | Q(expires__gte=now), **get_kwargs)
    if msg:
        if expires:
            # Update the expiration time
            msg.update(expires=expires)
    else:
        Message(**get_kwargs).save()

from django.db import models

from .feedback import Feedback
from ..regions.region import Region


class OfferListFeedback(Feedback):
    """
    Database model representing feedback about the offer list (e.g. missing offers).

    Fields inherited from the base model :class:`~cms.models.feedback.feedback.Feedback`:

    :param id: The database id of the feedback
    :param emotion: Whether the feedback is positive or negative (choices: :mod:`cms.constants.feedback_emotions`)
    :param comment: A comment describing the feedback
    :param is_technical: Whether or not the feedback is targeted at the developers
    :param read_status: Whether or not the feedback is marked as read
    :param created_date: The date and time when the feedback was created
    :param last_updated: The date and time when the feedback was last updated

    Relationship fields:

    :param region: The region to which offer list the feedback is referring to (related name: ``offer_list_feedback``)
    :param feedback_ptr: A pointer to the base class
    """

    region = models.ForeignKey(
        Region, related_name="offer_list_feedback", on_delete=models.CASCADE
    )

    class Meta:
        default_permissions = ()

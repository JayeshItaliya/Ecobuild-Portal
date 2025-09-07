from django.db import models
from django.db.models import JSONField
 
from backend.models import BaseTranslatableModel
 

class FAQ(BaseTranslatableModel):
    question = JSONField(default=dict, help_text="The frequently asked question")
    answer = JSONField(default=dict, help_text="The answer to the question")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True, help_text="Whether this FAQ is currently displayed"
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Display order (lower numbers appear first)"
    )

    TRANSLATABLE_FIELDS = ["question", "answer"]

    def __str__(self):
        if isinstance(self.question, dict):
            return self.question.get("en") or next(
                iter(self.question.values()), "Unnamed FAQ"
            )
        return str(self.question)

    class Meta:
        db_table = "faq"
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["order", "created_at"]

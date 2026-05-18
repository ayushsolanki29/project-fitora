from django.db import models


class ChatMessage(models.Model):
  ROLE_CHOICES = [
      ('user', 'User'),
      ('assistant', 'Assistant'),
  ]

  session_key = models.CharField(max_length=64, db_index=True)
  customer_id = models.IntegerField(null=True, blank=True)
  role = models.CharField(max_length=20, choices=ROLE_CHOICES)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
      ordering = ['created_at']

  def __str__(self):
      return f'{self.role}: {self.content[:50]}'

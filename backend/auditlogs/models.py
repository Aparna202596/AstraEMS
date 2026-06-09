from mongoengine import Document, StringField, DateTimeField, DictField
from datetime import datetime, timezone


class AuditLog(Document):
    user_email  = StringField(required=True)
    user_role   = StringField(required=True)
    action      = StringField(required=True)   # 'login', 'signup', 'logout', 'approve_user', etc.
    module      = StringField(required=True)   # 'auth', 'employees', 'assets', etc.
    description = StringField()
    ip_address  = StringField()
    extra_data  = DictField()                  # any additional JSON context
    timestamp   = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'audit_logs',
        'ordering': ['-timestamp'],
        'indexes': ['user_email', 'user_role', 'action', 'timestamp'],
    }

    def __str__(self):
        return f"[{self.timestamp}] {self.user_role}:{self.user_email} — {self.action}"
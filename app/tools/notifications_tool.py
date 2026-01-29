"""
Simple notification tool for high-severity complaints
Simulates email/Slack notifications (no actual sending for demo)
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationTool:
    """
    Simulates sending notifications for escalated complaints
    In production: Integrate with actual email/Slack APIs
    """
    
    def __init__(self):
        self.notification_log = []
    
    def send_escalation_alert(
        self,
        complaint_id: str,
        guest_name: str,
        room_number: str,
        severity: str,
        category: str,
        key_issues: list,
        assigned_department: str
    ) -> bool:
        """
        Send escalation notification to relevant staff
        
        Args:
            complaint_id: Unique complaint identifier
            guest_name: Guest name
            room_number: Room number
            severity: Severity level
            category: Complaint category
            key_issues: List of key issues
            assigned_department: Department handling the complaint
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Determine recipients based on severity and category
            recipients = self._get_recipients(severity, category, assigned_department)
            
            # Build notification message
            message = self._build_message(
                complaint_id=complaint_id,
                guest_name=guest_name,
                room_number=room_number,
                severity=severity,
                category=category,
                key_issues=key_issues,
                assigned_department=assigned_department
            )
            
            # Log notification (simulated - in production, actually send)
            notification_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "complaint_id": complaint_id,
                "recipients": recipients,
                "message": message,
                "status": "sent"
            }
            
            self.notification_log.append(notification_record)
            
            logger.info(f"📧 Escalation notification sent for complaint {complaint_id}")
            logger.info(f"   Recipients: {', '.join(recipients)}")
            
            # In production, actually send:
            # - Email via SMTP or SendGrid
            # - Slack via webhook
            # - SMS via Twilio
            # send_email(recipients, subject, message)
            # post_to_slack(channel, message)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Notification failed: {e}")
            return False
    
    def _get_recipients(self, severity: str, category: str, department: str) -> list:
        """Determine who should be notified"""
        recipients = []
        
        # Always notify assigned department
        dept_emails = {
            "Engineering": ["engineering.manager@hotel.com"],
            "Housekeeping": ["housekeeping.manager@hotel.com"],
            "Front Desk": ["frontdesk.manager@hotel.com"],
            "Guest Relations": ["guestrelations@hotel.com"],
            "Maintenance": ["maintenance@hotel.com"]
        }
        
        # Add department contacts
        for dept in department.split(","):
            dept = dept.strip()
            if dept in dept_emails:
                recipients.extend(dept_emails[dept])
        
        # For critical cases, escalate to senior management
        if severity == "critical":
            recipients.extend([
                "gm@hotel.com",  # General Manager
                "operations.director@hotel.com"
            ])
        elif severity == "high":
            recipients.append("duty.manager@hotel.com")
        
        return list(set(recipients))  # Remove duplicates
    
    def _build_message(
        self,
        complaint_id: str,
        guest_name: str,
        room_number: str,
        severity: str,
        category: str,
        key_issues: list,
        assigned_department: str
    ) -> str:
        """Build notification message"""
        
        emoji = "🚨" if severity == "critical" else "⚠️" if severity == "high" else "ℹ️"
        
        message = f"""{emoji} GUEST COMPLAINT ALERT - {severity.upper()} PRIORITY

Complaint ID: {complaint_id}
Guest: {guest_name}
Room: {room_number}
Category: {category}
Assigned To: {assigned_department}

Key Issues:
{chr(10).join(f"  • {issue}" for issue in key_issues)}

Action Required: Immediate attention needed. Check complaint management system for full details and action plan.

---
This is an automated notification from the Hotel Complaint Management System.
"""
        return message
    
    def get_notification_history(self, complaint_id: str = None) -> list:
        """Retrieve notification history"""
        if complaint_id:
            return [n for n in self.notification_log if n["complaint_id"] == complaint_id]
        return self.notification_log


# Singleton instance
notification_tool = NotificationTool()
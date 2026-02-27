"""
Alert Service for sending automatic notifications
- High usage alerts
- Leak detection alerts
- Daily usage updates
- Threshold warnings
"""

from .sms_service import send_sms
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AlertService:
    """
    Service for sending automated alerts to users via SMS
    """
    
    @staticmethod
    def send_meter_alert(user_phone: str, meter_reading: float, alert_type: str, **kwargs) -> bool:
        """
        Send meter reading alert to user
        
        Args:
            user_phone: User's phone number (+919876543210)
            meter_reading: Current meter reading in liters
            alert_type: Type of alert (high_usage, leak_detected, threshold, daily_update)
            **kwargs: Additional parameters (threshold, daily_limit, etc.)
            
        Returns:
            bool: True if SMS sent successfully
        """
        
        # Alert message templates
        messages = {
            'high_usage': (
                f"⚠️ Gram Meter Alert: High water usage detected! "
                f"Current reading: {meter_reading:.1f}L. "
                f"Please check for leaks or excessive usage."
            ),
            'leak_detected': (
                f"🚨 URGENT - Gram Meter Alert: Possible water leak detected! "
                f"Continuous flow detected. Reading: {meter_reading:.1f}L. "
                f"Please check your water lines immediately."
            ),
            'threshold': (
                f"📊 Gram Meter Alert: You've reached {meter_reading:.1f}L usage. "
                f"Threshold: {kwargs.get('threshold', 'N/A')}L. "
                f"Please monitor your consumption."
            ),
            'daily_update': (
                f"📈 Gram Meter Daily Update: Today's water usage is {meter_reading:.1f}L. "
                f"Target: {kwargs.get('daily_limit', 'N/A')}L. "
                f"Keep up the good work!"
            ),
            'monthly_summary': (
                f"📊 Gram Meter Monthly Summary: Total usage: {meter_reading:.1f}L. "
                f"Average daily: {kwargs.get('daily_avg', 'N/A')}L. "
                f"Thank you for being water conscious!"
            ),
            'low_balance': (
                f"💰 Gram Meter Alert: Your prepaid balance is low. "
                f"Current: ₹{kwargs.get('balance', 'N/A')}. "
                f"Please recharge to avoid service interruption."
            ),
            'payment_success': (
                f"✅ Gram Meter: Payment successful! "
                f"Amount: ₹{kwargs.get('amount', 'N/A')}. "
                f"New balance: ₹{kwargs.get('new_balance', 'N/A')}. "
                f"Thank you!"
            ),
            'meter_offline': (
                f"⚠️ Gram Meter Alert: Your meter at {kwargs.get('location', 'your location')} "
                f"is offline. Last reading: {meter_reading:.1f}L. "
                f"Please check the connection."
            ),
        }
        
        message = messages.get(
            alert_type,
            f"Gram Meter Alert: Current reading {meter_reading:.1f}L"
        )
        
        try:
            result = send_sms(user_phone, message)
            
            if result['success']:
                logger.info(f"Alert sent to {user_phone}: {alert_type} via {result.get('provider')}")
                return True
            else:
                logger.warning(f"Failed to send alert to {user_phone}: {result.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"Exception sending alert to {user_phone}: {str(e)}")
            return False
    
    @staticmethod
    def send_bulk_alerts(user_phones: list, message: str) -> dict:
        """
        Send alert to multiple users
        
        Args:
            user_phones: List of phone numbers
            message: Alert message
            
        Returns:
            dict: {'success': int, 'failed': int, 'results': list}
        """
        success_count = 0
        failed_count = 0
        results = []
        
        for phone in user_phones:
            try:
                result = send_sms(phone, message)
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
                results.append({
                    'phone': phone,
                    'status': 'success' if result['success'] else 'failed',
                    'message': result.get('message')
                })
            except Exception as e:
                failed_count += 1
                results.append({
                    'phone': phone,
                    'status': 'failed',
                    'message': str(e)
                })
        
        logger.info(f"Bulk alert sent: {success_count} success, {failed_count} failed")
        
        return {
            'success': success_count,
            'failed': failed_count,
            'results': results
        }
    
    @staticmethod
    def send_otp_alert(phone_number: str, otp_code: str, expires_minutes: int = 5) -> dict:
        """
        Send OTP via SMS
        
        Args:
            phone_number: Recipient phone number
            otp_code: 6-digit OTP code
            expires_minutes: OTP validity in minutes
            
        Returns:
            dict: Result from SMS service
        """
        message = (
            f"🔐 Your Gram Meter OTP is: {otp_code}\n"
            f"Valid for {expires_minutes} minutes. "
            f"Do not share this code with anyone."
        )
        
        return send_sms(phone_number, message)
    
    @staticmethod
    def send_welcome_message(phone_number: str, username: str) -> bool:
        """
        Send welcome message to new user
        
        Args:
            phone_number: User's phone number
            username: User's name
            
        Returns:
            bool: True if sent successfully
        """
        message = (
            f"🌾 Welcome to Gram Meter, {username}! "
            f"Your smart water meter is now active. "
            f"Track usage, get alerts, and save water. "
            f"Login at grammeter.in"
        )
        
        try:
            result = send_sms(phone_number, message)
            return result['success']
        except Exception as e:
            logger.error(f"Failed to send welcome message: {str(e)}")
            return False


# Convenience function
def send_alert(phone_number: str, meter_reading: float, alert_type: str, **kwargs) -> bool:
    """Send alert to user"""
    return AlertService.send_meter_alert(phone_number, meter_reading, alert_type, **kwargs)

"""
Unified SMS Service supporting multiple providers
- Fast2SMS (India - Recommended)
- AWS SNS (Pay-per-use)
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """
    Unified SMS service supporting multiple providers
    Send OTPs and alerts to any mobile number
    """
    
    @staticmethod
    def send_sms(phone_number: str, message: str) -> dict:
        """
        Send SMS using configured provider
        
        Args:
            phone_number: Recipient phone number with country code (+919876543210)
            message: SMS message content
            
        Returns:
            dict: {'success': bool, 'message': str, 'provider': str}
        """
        provider = getattr(settings, 'SMS_PROVIDER', 'FAST2SMS')
        
        try:
            if provider == 'FAST2SMS':
                return SMSService._send_fast2sms(phone_number, message)
            elif provider == 'AWS_SNS':
                return SMSService._send_aws_sns(phone_number, message)
            else:
                raise ValueError("Unsupported SMS provider")
        except Exception as e:
            logger.error(f"SMS send failed with {provider}: {str(e)}")
            return {
                'success': False,
                'message': f'SMS sending failed: {str(e)}',
                'provider': provider
            }
    
    @staticmethod
    def _send_fast2sms(phone_number: str, message: str) -> dict:
        """Send SMS via Fast2SMS (India)"""
        if not getattr(settings, 'FAST2SMS_API_KEY', None):
            return {
                'success': False,
                'message': 'Fast2SMS API Key not configured',
                'provider': 'FAST2SMS'
            }

        try:
            # Normalize Indian number to last 10 digits
            digits = ''.join(ch for ch in phone_number if ch.isdigit())
            mobile = digits[-10:] if len(digits) >= 10 else digits

            # Try to extract 6-digit OTP from message if present
            import re
            match = re.search(r"\b\d{6}\b", message)
            otp_code = match.group() if match else None

            headers = {
                'accept': 'application/json',
                'content-type': 'application/json',
                'authorization': settings.FAST2SMS_API_KEY,
            }

            url = 'https://www.fast2sms.com/dev/bulkV2'
            payload = {
                'route': 'q',
                'message': message,
                'flash': 0,
                'sms_details': 1,
                'numbers': mobile,
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            try:
                body = response.json()
            except Exception:
                body = {}
            ok = response.status_code == 200 and bool(body.get('return'))
            if ok:
                logger.info(f"Fast2SMS SMS sent to {mobile}")
                return {
                    'success': True,
                    'message': 'SMS sent successfully via Fast2SMS',
                    'provider': 'FAST2SMS'
                }
            else:
                logger.error(f"Fast2SMS failed ({response.status_code}): {response.text}")
                return {
                    'success': False,
                    'message': f'Fast2SMS error: {response.text}',
                    'provider': 'FAST2SMS'
                }
        except Exception as e:
            logger.error(f"Fast2SMS exception: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'provider': 'FAST2SMS'
            }
    
    @staticmethod
    def _send_aws_sns(phone_number: str, message: str) -> dict:
        """Send SMS via AWS SNS"""
        try:
            import boto3
            
            if not all([
                getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
            ]):
                return {
                    'success': False,
                    'message': 'AWS credentials not configured',
                    'provider': 'AWS_SNS'
                }
            
            sns = boto3.client(
                'sns',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_REGION', 'ap-south-1')
            )
            
            response = sns.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"AWS SNS sent: {response['MessageId']}")
            return {
                'success': True,
                'message': 'SMS sent successfully via AWS SNS',
                'provider': 'AWS_SNS',
                'message_id': response['MessageId']
            }
        except Exception as e:
            logger.error(f"AWS SNS exception: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'provider': 'AWS_SNS'
            }


# Convenience function for backward compatibility
def send_sms(phone_number: str, message: str) -> dict:
    """Send SMS using configured provider"""
    return SMSService.send_sms(phone_number, message)

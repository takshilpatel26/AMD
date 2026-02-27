"""
Notification Service - Twilio WhatsApp and SMS Integration
"""

from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """
    Service for sending notifications via Twilio (WhatsApp and SMS)
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_from = settings.TWILIO_WHATSAPP_NUMBER
        self.sms_from = settings.TWILIO_PHONE_NUMBER
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    def send_whatsapp(self, to_number, message, language='en'):
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number (str): Recipient phone number (with country code, e.g., +919876543210)
            message (str): Message text
            language (str): Language code (en, hi, gu)
        
        Returns:
            dict: Response with status and message_sid
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return {'success': False, 'error': 'Twilio not configured'}
        
        try:
            # Format WhatsApp number
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            # Send message
            message_obj = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"WhatsApp sent to {to_number}: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'channel': 'whatsapp'
            }
        
        except Exception as e:
            logger.error(f"WhatsApp send failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_sms(self, to_number, message, language='en'):
        """
        Send SMS via Twilio
        
        Args:
            to_number (str): Recipient phone number (with country code)
            message (str): Message text
            language (str): Language code (en, hi, gu)
        
        Returns:
            dict: Response with status and message_sid
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return {'success': False, 'error': 'Twilio not configured'}
        
        try:
            # Send SMS
            message_obj = self.client.messages.create(
                from_=self.sms_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'channel': 'sms'
            }
        
        except Exception as e:
            logger.error(f"SMS send failed: {str(e)}")
            return {'success': False, 'error': str(e)}


class AlertNotificationService:
    """
    Service for sending alert notifications in multiple languages
    """
    
    # Alert message templates in multiple languages
    ALERT_TEMPLATES = {
        'voltage_spike': {
            'en': "⚠️ VOLTAGE SPIKE ALERT\nMeter: {meter_id}\nVoltage: {voltage}V\nTime: {time}\nAction: Check voltage regulator immediately!",
            'hi': "⚠️ वोल्टेज स्पाइक अलर्ट\nमीटर: {meter_id}\nवोल्टेज: {voltage}V\nसमय: {time}\nकार्रवाई: तुरंत वोल्टेज रेगुलेटर की जांच करें!",
            'gu': "⚠️ વોલ્ટેજ સ્પાઇક ચેતવણી\nમીટર: {meter_id}\nવોલ્ટેજ: {voltage}V\nસમય: {time}\nકાર્યવાહી: તાત્કાલિક વોલ્ટેજ રેગ્યુલેટરની તપાસ કરો!"
        },
        'voltage_drop': {
            'en': "⚠️ LOW VOLTAGE ALERT\nMeter: {meter_id}\nVoltage: {voltage}V\nTime: {time}\nAction: Check main supply and connections.",
            'hi': "⚠️ कम वोल्टेज अलर्ट\nमीटर: {meter_id}\nवोल्टेज: {voltage}V\nसमय: {time}\nकार्रवाई: मुख्य आपूर्ति और कनेक्शन की जांच करें।",
            'gu': "⚠️ નીચું વોલ્ટેજ ચેતવણી\nમીટર: {meter_id}\nવોલ્ટેજ: {voltage}V\nસમય: {time}\nકાર્યવાહી: મુખ્ય સપ્લાય અને કનેક્શન્સ તપાસો।"
        },
        'overcurrent': {
            'en': "🔥 OVERCURRENT ALERT\nMeter: {meter_id}\nCurrent: {current}A\nTime: {time}\nAction: Reduce load immediately to prevent damage!",
            'hi': "🔥 ओवरकरंट अलर्ट\nमीटर: {meter_id}\nकरंट: {current}A\nसमय: {time}\nकार्रवाई: नुकसान से बचने के लिए तुरंत लोड कम करें!",
            'gu': "🔥 વધારે કરંટ ચેતવણી\nમીટર: {meter_id}\nકરંટ: {current}A\nસમય: {time}\nકાર્યવાહી: નુકસાન અટકાવવા તાત્કાલિક લોડ ઘટાડો!"
        },
        'phantom_load': {
            'en': "💡 PHANTOM LOAD DETECTED\nMeter: {meter_id}\nPower: {power}W at {time}\nAction: Check for appliances on standby. Save ₹{savings}/month!",
            'hi': "💡 फैंटम लोड का पता चला\nमीटर: {meter_id}\nपावर: {power}W, {time}\nकार्रवाई: स्टैंडबाय उपकरणों की जांच करें। ₹{savings}/माह बचाएं!",
            'gu': "💡 ફેન્ટમ લોડ મળ્યો\nમીટર: {meter_id}\nપાવર: {power}W, {time}\nકાર્યવાહી: સ્ટેન્ડબાય ઉપકરણો તપાસો। ₹{savings}/મહિને બચાવો!"
        },
        'power_outage': {
            'en': "🚨 POWER OUTAGE\nMeter: {meter_id}\nTime: {time}\nStatus: No power detected\nAction: Check main breaker and utility supply.",
            'hi': "🚨 बिजली कटौती\nमीटर: {meter_id}\nसमय: {time}\nस्थिति: बिजली नहीं मिली\nकार्रवाई: मुख्य ब्रेकर और यूटिलिटी आपूर्ति की जांच करें।",
            'gu': "🚨 પાવર આઉટેજ\nમીટર: {meter_id}\nસમય: {time}\nસ્થિતિ: પાવર મળ્યું નહીં\nકાર્યવાહી: મુખ્ય બ્રેકર અને યુટિલિટી સપ્લાય તપાસો।"
        },
        'high_consumption': {
            'en': "📊 HIGH CONSUMPTION ALERT\nMeter: {meter_id}\nEnergy: {energy}kWh\nCost: ₹{cost}\nAction: Review usage patterns to reduce bills.",
            'hi': "📊 उच्च खपत अलर्ट\nमीटर: {meter_id}\nऊर्जा: {energy}kWh\nलागत: ₹{cost}\nकार्रवाई: बिल कम करने के लिए उपयोग पैटर्न की समीक्षा करें।",
            'gu': "📊 વધારે વપરાશ ચેતવણી\nમીટર: {meter_id}\nઊર્જા: {energy}kWh\nખર્ચ: ₹{cost}\nકાર્યવાહી: બિલ ઘટાડવા વપરાશ પેટર્ન તપાસો।"
        }
    }
    
    def __init__(self):
        self.twilio_service = TwilioService()
    
    def send_alert(self, alert, user, channel='whatsapp'):
        """
        Send alert notification to user
        
        Args:
            alert (Alert): Alert model instance
            user (User): User model instance
            channel (str): 'whatsapp' or 'sms'
        
        Returns:
            dict: Response with status
        """
        # Get template for alert type and user's preferred language
        template = self.ALERT_TEMPLATES.get(alert.alert_type, {})
        language = user.preferred_language if hasattr(user, 'preferred_language') else 'en'
        message = template.get(language, template.get('en', ''))
        
        if not message:
            logger.error(f"No template found for alert type: {alert.alert_type}")
            return {'success': False, 'error': 'Template not found'}
        
        # Format message with alert data
        try:
            from django.utils import timezone
            
            message = message.format(
                meter_id=alert.meter.meter_id,
                voltage=alert.data.get('voltage', 'N/A') if alert.data else 'N/A',
                current=alert.data.get('current', 'N/A') if alert.data else 'N/A',
                power=alert.data.get('power', 'N/A') if alert.data else 'N/A',
                energy=alert.data.get('energy', 'N/A') if alert.data else 'N/A',
                cost=alert.estimated_cost_impact if alert.estimated_cost_impact else 'N/A',
                savings=int(alert.estimated_cost_impact) if alert.estimated_cost_impact else 100,
                time=timezone.localtime(alert.created_at).strftime('%d/%m/%Y %H:%M')
            )
        except Exception as e:
            logger.error(f"Message formatting failed: {str(e)}")
            message = f"Alert: {alert.alert_type} - {alert.message}"
        
        # Get user's phone number
        phone_number = user.phone if hasattr(user, 'phone') else None
        if not phone_number:
            logger.error(f"No phone number for user: {user.username}")
            return {'success': False, 'error': 'No phone number'}
        
        # Ensure phone number has country code
        if not phone_number.startswith('+'):
            phone_number = f'+91{phone_number}'  # Default to India (+91)
        
        # Send notification
        if channel == 'whatsapp':
            result = self.twilio_service.send_whatsapp(phone_number, message, language)
        else:
            result = self.twilio_service.send_sms(phone_number, message, language)
        
        # Create notification record
        if result.get('success'):
            from .models import Notification
            Notification.objects.create(
                user=user,
                alert=alert if hasattr(alert, 'id') else None,
                channel=channel,
                message=message,
                status='sent',
                external_id=result.get('message_sid')
            )
        
        return result
    
    def send_bulk_alert(self, alert, users, channel='whatsapp'):
        """
        Send alert to multiple users
        
        Args:
            alert (Alert): Alert model instance
            users (QuerySet): User queryset
            channel (str): 'whatsapp' or 'sms'
        
        Returns:
            dict: Summary of sent notifications
        """
        results = {
            'total': users.count(),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for user in users:
            result = self.send_alert(alert, user, channel)
            if result.get('success'):
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'user': user.username,
                    'error': result.get('error')
                })
        
        logger.info(f"Bulk alert sent: {results['sent']}/{results['total']} successful")
        return results


# Singleton instances
twilio_service = TwilioService()
alert_notification_service = AlertNotificationService()

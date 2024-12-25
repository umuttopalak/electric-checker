from app import mail, bot
from flask_mail import Message
from app.utils.logger import log_message
from app.models.log import LogTypeEnum

async def send_information(subject, recipient, body, chat_id):
    try:
        # Send email
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=body
        )
        mail.send(msg)
        log_message(
            level="INFO", 
            message=f"Email sent to {recipient}", 
            log_type=LogTypeEnum.NOTIFICATION_EMAIL_SENT
        )
    except Exception as e:
        log_message(
            level="ERROR",
            message=f"Error sending mail to: {recipient} - {str(e)}",
            log_type=LogTypeEnum.ERROR_NOTIFICATION
        )

    # Send telegram message
    try:
        await bot.send_message(chat_id=chat_id, text=body)
        log_message(
            level="INFO",
            message=f"Telegram message sent to {chat_id}",
            log_type=LogTypeEnum.NOTIFICATION_TELEGRAM_SENT
        )
    except Exception as e:
        log_message(
            level="ERROR",
            message=f"Error sending telegram message to: {chat_id} - {str(e)}",
            log_type=LogTypeEnum.ERROR_NOTIFICATION
        ) 
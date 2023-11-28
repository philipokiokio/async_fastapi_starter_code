import groundible_admin.services.service_utils.token_utils as gr_toks_utils
import groundible_admin.services.service_utils.gr_redis_utils as redis_utils
from groundible_admin.root.utils.mailer import send_mail


async def invite_agent(email: str):
    token: int = gr_toks_utils.gr_token_gen()

    redis_utils.add_admin_invite_token(token=token, email=email)
    # send email optional
    await send_mail(
        subject="Invitation to Groundible",
        reciepients=[email],
        payload={"token": token},
        template="user_auth/token_email_template.html",
    )
    return {"token": token}

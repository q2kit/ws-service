from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from django.core.cache import cache


class VerifyEmailMessageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # check if message exists in request
        for msg_str in [msg.message for msg in messages.get_messages(request)]:
            if "Please verify your email address" in msg_str:
                return
        if self.should_add_message(request):
            messages.warning(
                request,
                format_html(f"""
                    Please verify your email address before you can use the service.
                    <a href='{reverse('verify')}?next={request.path}'>Verify now</a>
                """)
            )

    def should_add_message(self, request):
        except_paths = [
            reverse('signup'),
            reverse('verify'),
        ]
        except_keywords = [
            'admin/jsi18n',
            'password_reset',
        ]
        should = [request.user.is_authenticated and not request.user.verified]
        should.append(request.path not in except_paths)
        should.append(not any(keyword in request.path for keyword in except_keywords))
        should.append(cache.get(f"verify_email_notice_{request.user.id}") is None)
        return all(should)

import os
import django
from django.core.asgi import get_asgi_application
from django.conf import settings
from django.core.files.storage import default_storage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import websocket.routing


class MediaFileServer:
    async def __call__(self, scope, receive, send):
        path = scope['path']
        if path.startswith(settings.MEDIA_URL):
            file_path = path[len(settings.MEDIA_URL):]
            try:
                if default_storage.exists(file_path):
                    file = default_storage.open(file_path)
                    content = file.read()
                    file.close()
                    ext = file_path.split('.')[-1].lower()
                    content_types = {
                        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'png': 'image/png', 'gif': 'image/gif',
                        'webp': 'image/webp', 'svg': 'image/svg+xml',
                    }
                    content_type = content_types.get(ext, 'application/octet-stream')
                    await send({
                        'type': 'http.response.start',
                        'status': 200,
                        'headers': [[b'content-type', content_type.encode()]],
                    })
                    await send({
                        'type': 'http.response.body',
                        'body': content,
                    })
                    return
            except Exception:
                pass
            await send({
                'type': 'http.response.start',
                'status': 404,
                'headers': [[b'content-type', b'text/html']],
            })
            await send({
                'type': 'http.response.body',
                'body': b'Not Found',
            })
            return
        
        django_app = get_asgi_application()
        await django_app(scope, receive, send)


application = ProtocolTypeRouter({
    "http": MediaFileServer(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket.routing.websocket_urlpatterns
        )
    ),
})

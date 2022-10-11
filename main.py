from a2wsgi import ASGIMiddleware
from app import app

WSGI_APP = ASGIMiddleware(app)

# Force location of zagg-web handler into path
import sys
sys.path.insert(0, '/var/www/zagg2')
from zagg2 import flask_app as application

# Allow logging/errors to show up in Apache logs
import logging, sys
logging.basicConfig(stream=sys.stderr)

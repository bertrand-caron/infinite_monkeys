from typing import Optional, Any
from flask import Flask

from models import db

def create_app(config: Optional[Any] = None, environment: Optional[Any] = None) -> Any:
    app = Flask(__name__)

    app.config['ENVIRONMENT'] = environment
    app.config.update(config or {})

    db.init_app(app)

    return app

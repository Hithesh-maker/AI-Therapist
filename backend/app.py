import logging
import os

from flask import Flask
from flask_cors import CORS

from backend.config import ALLOWED_ORIGINS, FRONTEND_ROOT
from backend.routes.main import bp as main_bp
from backend.utils.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_folder=str(FRONTEND_ROOT / "static"),
    template_folder=str(FRONTEND_ROOT),
)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["JSON_SORT_KEYS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = False

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})
app.register_blueprint(main_bp)


@app.errorhandler(404)
def not_found(_error):
    return {"success": False, "error": "Not found"}, 404


@app.errorhandler(500)
def server_error(_error):
    return {"success": False, "error": "Internal server error"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))




# ================= RUN =================


if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )
from waitress import serve
import app  # або from app import app, якщо твій Flask додаток оголошений як `app = Flask(__name__)`

serve(app.app, host="0.0.0.0", port=8000)


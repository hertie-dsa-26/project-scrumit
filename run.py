from app import create_app
from app.config import DevelopmentConfig
import sys

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app = create_app(DevelopmentConfig)
    app.run(debug=True, host='0.0.0.0', port=port)

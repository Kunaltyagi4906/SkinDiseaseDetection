

import os

from skindisease import app, initialize_database

# Create tables if not already created
initialize_database()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))



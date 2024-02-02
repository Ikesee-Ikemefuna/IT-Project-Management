from flask import Flask, render_template, send_from_directory
from app import app

# Create Flask app
main_app = Flask(__name__)

# Register the 'app' blueprint
main_app.register_blueprint(app)

# Serve static files (CSS, JS, images, etc.)
@main_app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Serve the Shop_product_finder.sql file
@main_app.route('/database/Shop_product_finder.sql')
def serve_database():
    return send_from_directory('database', 'Shop_product_finder.sql')

# Serve JS files from the 'js' folder
@main_app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

# Serve CSS files from the 'css' folder
@main_app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

# Serve images from the 'images' folder
@main_app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

# Define the main route
@main_app.route('/')
def main():
    return render_template('main/index.html')

if __name__ == '__main__':
    main_app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from html import escape
from flask import session

def sanitize_input(value):
    return escape(value)

app = Flask(__name__)

# Configure MySQL
app.secret_key = '123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'shop_product_finder'

mysql = MySQL(app)

# Define user types
CUSTOMER = 'customer'
INVENTORY_MANAGER = 'inventory_manager'
ADMIN = 'admin'

# Restrict access to the root URL
@app.route('/')
def index():
    # Redirect to the customer login page
    return redirect(url_for('customer_login'))

# Frontend routes
@app.route('/home')
def home():
    return render_template('customer/home.html')

@app.route('/about')
def about():
    return render_template('customer/about.html')

@app.route('/contact')
def contact():
    return render_template('customer/contact.html')

# Customer routes
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
        
        # Verify the user's credentials
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # Set session variables
            session['user_id'] = user[0]
            session['user_type'] = CUSTOMER
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('customer/login.html')


@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
              
        # Check if the username is already taken
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        cur.close()
        
        if existing_user:
            flash('Username is already taken. Please choose another one.', 'danger')
        else:
            # Insert the new user into the 'users' table
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO users (username, password, user_type)
                VALUES (%s, %s, 'customer')
            """, (username, password))
            mysql.connection.commit()
            cur.close()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('customer_login'))

    return render_template('customer/register.html')

@app.route('/customer/logout')
def customer_logout():
    # Check if the user is logged in
    if 'user_id' in session:
        # Clear the user session data
        session.pop('user_id', None)
        session.pop('user_type', None)

    # Redirect to the login page
    return redirect(url_for('customer_login') if 'user_id' not in session else url_for('home'))

@app.route('/customer/product_list')
def customer_product_list():
    try:
        # Fetch all products and their shops
        cur = mysql.connection.cursor()

        # Fetching Products
        cur.execute("SELECT * FROM products")
        products_columns = [desc[0] for desc in cur.description]
        products_data = cur.fetchall()

        # Fetching Shops
        cur.execute("SELECT * FROM shops")
        shops_columns = [desc[0] for desc in cur.description]
        shops_data = cur.fetchall()

        cur.close()

        return render_template('customer/product_list.html',
                                products_columns=products_columns,
                               products_data=products_data,
                               shops_columns=shops_columns,
                               shops_data=shops_data)
    except Exception as e:
        print("Error fetching data:", str(e))
        return "An error occurred while fetching data from the database."

######################################################################################################################
# Inventory Manager routes
@app.before_request
def check_access():
    # Define a list of routes that require login as an inventory manager
    inventory_manager_routes = [
        'inventory_manager_dashboard',
        'inventory_manager_add_product',
        'inventory_manager_edit_product',
        'inventory_manager_delete_product',
    ]

    # Define a list of routes that require login as an admin
    admin_routes = [
        'admin_dashboard',
        'admin_add_shop',
        'admin_edit_shop',
        'admin_delete_shop',
        # Add more admin routes as needed
    ]

    # Check if the current route requires inventory manager or admin access
    if request.endpoint:
        if request.endpoint in inventory_manager_routes and ('user_id' not in session or session.get('user_type') != 'inventory_manager'):
            flash('Access restricted. Please log in as an inventory manager.', 'warning')
            return redirect(url_for('inventory_manager_login'))

        elif request.endpoint in admin_routes and ('user_id' not in session or session.get('user_type') != 'admin'):
            flash('Access restricted. Please log in as an admin.', 'warning')
            return redirect(url_for('admin_login')) 


@app.route('/inventory_manager/login', methods=['GET', 'POST'])
def inventory_manager_login():
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])

        # Verify the inventory manager's credentials
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s AND user_type = 'inventory_manager'",
                    (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Set session variables
            session['user_id'] = user[0]
            session['user_type'] = INVENTORY_MANAGER
            return redirect(url_for('inventory_manager_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('inventory_manager/login.html')

# Inventory Manager route for registration
@app.route('/inventory_manager/register', methods=['GET', 'POST'])
def inventory_manager_register():
    if request.method == 'POST':
        # Get form data
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])

        # Check if the username is already taken
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash('Username is already taken. Please choose another one.', 'danger')
        else:
            # Insert the new inventory manager into the 'users' table with 'inventory_manager' user_type
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO users (username, password, user_type)
                VALUES (%s, %s, 'inventory_manager')
            """, (username, password))
            mysql.connection.commit()
            cur.close()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('inventory_manager_login'))

    return render_template('inventory_manager/register.html')

# Inventory Manager logout
@app.route('/inventory_manager/logout')
def inventory_manager_logout():
    # Check if the inventory manager is logged in
    if 'manager_id' in session:
        # Clear the inventory manager session data
        session.pop('manager_id', None)

        flash('Inventory Manager logout successful. See you next time!', 'info')
    return redirect(url_for('inventory_manager_login'))

# Inventory Manager route for dashboard
@app.route('/inventory_manager/dashboard')
def inventory_manager_dashboard():
    # Check if the user is logged in as an inventory manager
    if 'user_id' in session and session['user_type'] == INVENTORY_MANAGER:
        try:
            # Fetch all products and their shops
            cur = mysql.connection.cursor()

            # Fetching Products
            cur.execute("SELECT * FROM products")
            products_columns = [desc[0] for desc in cur.description]
            products_data = cur.fetchall()

            # Fetching Shops
            cur.execute("SELECT * FROM shops")
            shops_columns = [desc[0] for desc in cur.description]
            shops_data = cur.fetchall()

            cur.close()

            return render_template('inventory_manager/dashboard.html',
                                    products_columns=products_columns,
                                    products_data=products_data,
                                    shops_columns=shops_columns,
                                    shops_data=shops_data)
        except Exception as e:
            print("Error fetching data:", str(e))
            return "An error occurred while fetching data from the database."



# Inventory Manager route for adding a new product
@app.route('/inventory_manager/add_product', methods=['GET', 'POST'])
def inventory_manager_add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_image_url = request.form['product_image_url']
        price = float(request.form['price'])
        shop_id = int(request.form['shop_id'])
        quantity = int(request.form['quantity'])  # Added quantity field

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products (product_name, product_image_url, price, shop_id, quantity) 
            VALUES (%s, %s, %s, %s, %s)
        """, (product_name, product_image_url, price, shop_id, quantity))
        mysql.connection.commit()
        cur.close()

        flash('Product added successfully', 'success')
        return redirect(url_for('inventory_manager_dashboard'))

    # Fetch shop data to populate in the form
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shops")
    shops = cur.fetchall()
    cur.close()

    return render_template('inventory_manager/add_product.html', shops=shops)

# Inventory Manager route for editing product
@app.route('/inventory_manager/edit_product/<int:product_id>', methods=['GET', 'POST'])
def inventory_manager_edit_product(product_id):
    if request.method == 'POST':
        # Handle form submission to update product details in the database
        product_name = request.form['product_name']
        product_image_url = request.form['product_image_url']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        status = request.form['status']
        shop_id = int(request.form['shop_id'])

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE products 
            SET product_name=%s, product_image_url=%s, price=%s, quantity=%s, status=%s, shop_id=%s
            WHERE product_id=%s
        """, (product_name, product_image_url, price, quantity, status, shop_id, product_id))
        mysql.connection.commit()
        cur.close()

        flash('Product details updated successfully', 'success')
        return redirect(url_for('inventory_manager_dashboard'))

    # Fetch current product details to populate the edit form
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    product = cur.fetchone()
    cur.close()

    # Fetch shop data to populate the edit form
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shops")
    shops = cur.fetchall()
    cur.close()

    return render_template('inventory_manager/edit_product.html', product=product, shops=shops)



@app.route('/inventory_manager/delete_product/<int:product_id>', methods=['POST'])
def inventory_manager_delete_product(product_id):
    # Handle product deletion
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()

    flash('Product deleted successfully', 'success')
    return redirect(url_for('inventory_manager_dashboard'))



#################################################################################################

# Import necessary modules and classes

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = sanitize_input(request.form['username'])
        password = sanitize_input(request.form['password'])
        
        # Verify the admin's credentials
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()
        cur.close()
        
        if admin:
            # Set session variables
            session['user_id'] = admin[0]
            session['user_type'] = ADMIN
            flash('Login successful. Welcome!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/register')
def admin_register():
    return render_template('admin/register.html')

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    # Check if the admin is logged in
    if 'admin_id' in session:
        # Clear the admin session data
        session.pop('admin_id', None)

        flash('Admin logout successful. See you next time!', 'info')
    return redirect(url_for('admin_login'))

# Admin route for dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Fetch all shops and their products
    cur = mysql.connection.cursor()

    # Fetch shops
    cur.execute("SELECT * FROM shops")
    shops_data = cur.fetchall()
    shops_columns = [column[0] for column in cur.description]

    # Fetch products
    cur.execute("SELECT * FROM products")
    products_data = cur.fetchall()
    products_columns = [column[0] for column in cur.description]

    cur.close()

    return render_template(
        'admin/dashboard.html',
        shops_data=shops_data,
        shops_columns=shops_columns,
        products_data=products_data,
        products_columns=products_columns
    )

    
@app.route('/admin/add_shop', methods=['GET', 'POST'])
def admin_add_shop():
    if request.method == 'POST':
        shop_name = request.form['shop_name']
        shop_image_url = request.form['shop_image_url']
        shop_location = request.form['shop_location']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO shops (shop_name, shop_image_url, shop_location) VALUES (%s, %s, %s)",
                    (shop_name, shop_image_url, shop_location))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_shop.html')

@app.route('/admin/edit_shop/<int:shop_id>', methods=['GET', 'POST'])
def admin_edit_shop(shop_id):
    if request.method == 'POST':
        # Handle form submission to update shop details in the database
        shop_name = request.form['shop_name']
        shop_image_url = request.form['shop_image_url']
        shop_location = request.form['shop_location']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE shops SET shop_name=%s, shop_image_url=%s, shop_location=%s WHERE shop_id=%s",
                    (shop_name, shop_image_url, shop_location, shop_id))
        mysql.connection.commit()
        cur.close()

        flash('Shop details updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch current shop details to populate the edit form
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shops WHERE shop_id=%s", (shop_id,))
    shop = cur.fetchone()
    cur.close()

    return render_template('admin/edit_shop.html', shop=shop)


@app.route('/admin/delete_shop/<int:shop_id>', methods=['POST'])
def admin_delete_shop(shop_id):
    # Handle shop deletion
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM shops WHERE shop_id=%s", (shop_id,))
    mysql.connection.commit()
    cur.close()

    flash('Shop deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

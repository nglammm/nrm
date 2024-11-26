import pymysql
import os

# Database connection details
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')

def get_connection():
    """Establish and return a database connection."""
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=int(PORT)
    )

def fetch_data():
    """
    Fetch all data from the packages table.
    Returns a list of records.
    """
    records = []
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = "SELECT * FROM packages"
            cursor.execute(query)
            records = cursor.fetchall()
            print(f"Total number of rows in table: {cursor.rowcount}")

            for row in records:
                print(row)
    
    except Exception as e:
        print("Error while fetching data from MySQL:", e)
    
    finally:
        if connection:
            connection.close()
    
    return records

def search_package(package_name):
    """
    Search for a package by name in the database.
    Returns the first matching record or None if not found.
    """
    return search_by_column("package_name", package_name)

def search_owner(package_owner):
    """
    Search for packages by owner in the database.
    Returns a list of matching records or None if not found.
    """
    return search_by_column("package_owner", package_owner)

def search_link(package_link):
    """
    Search for packages by link in the database.
    Returns a list of matching records or None if not found.
    """
    return search_by_column("package_link", package_link)

def search_by_column(column_name, value):
    """
    Generic function to search for a package or owner by a specified column.
    Returns the matching records.
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = f"SELECT * FROM packages WHERE {column_name} = %s"
            cursor.execute(query, (value,))
            records = cursor.fetchall()

            if records:
                return records
            else:
                return None
    
    except Exception as e:
        print("Error while searching in MySQL:", e)
    
    finally:
        if connection:
            connection.close()

def insert_data(package_link, package_name, package_version, package_description, package_owner):
    """
    Insert a new package record into the database.
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """INSERT INTO packages (package_link, package_name, package_version, package_description, package_owner) 
                       VALUES (%s, %s, %s, %s, %s)"""
            
            # Debugging: Print the query and values 
            cursor.execute(query, (package_link, package_name, package_version, package_description, package_owner))
            connection.commit()

    except Exception as e:
        print("Error while inserting data into MySQL:", e)
    
    finally:
        if connection:
            connection.close()

def delete_package(package_name):
    """
    Delete a package from the database by package_name.
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = "DELETE FROM packages WHERE package_name = %s"
            cursor.execute(query, (package_name,))
            connection.commit()

            if cursor.rowcount > 0:
                print(f"Package '{package_name}' deleted successfully.")
            else:
                print(f"No package found with the name '{package_name}'.")

    except Exception as e:
        print("Error while deleting package from MySQL:", e)
    
    finally:
        if connection:
            connection.close()

def edit_package(package_name, new_name=None, new_version=None, new_description=None, new_owner=None):
    """
    Edit an existing package in the database.
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            updates = []
            values = []

            if new_name:
                updates.append("package_name = %s")
                values.append(new_name)
            if new_version:
                updates.append("package_version = %s")
                values.append(new_version)
            if new_description:
                updates.append("package_description = %s")
                values.append(new_description)
            if new_owner:
                updates.append("package_owner = %s")
                values.append(new_owner)

            if not updates:
                print("No updates provided.")
                return
            
            values.append(package_name)  # Append the package name for the WHERE clause
            query = f"UPDATE packages SET {', '.join(updates)} WHERE package_name = %s"
            cursor.execute(query, tuple(values))
            connection.commit()

            if cursor.rowcount > 0:
                print(f"Package '{package_name}' updated successfully.")
            else:
                print(f"No package found with the name '{package_name}'.")

    except Exception as e:
        print("Error while updating package in MySQL:", e)

    finally:
        if connection:
            connection.close()
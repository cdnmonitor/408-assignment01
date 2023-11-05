import sqlite3
import csv
import os

DATABASE_NAME = 'StudentDB.sqlite'

# create connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}, SQLite version {sqlite3.version}")
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    try:
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            StudentId INTEGER PRIMARY KEY,
            FirstName TEXT,
            LastName TEXT,
            GPA REAL,
            Major TEXT,
            FacultyAdvisor TEXT,
            Address TEXT,
            City TEXT,
            State TEXT,
            ZipCode TEXT,
            MobilePhoneNumber TEXT,
            isDeleted INTEGER
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def import_from_students_csv(conn):
    csv_file_name = 'students.csv'
    if os.path.isfile(csv_file_name):
        try:
            import_students_from_csv(csv_file_name, conn)
        except Exception as e:
            print(f"An error occurred while importing from CSV: {e}")
    else:
        print("The 'students.csv' file does not exist in the current directory.")

def import_students_from_csv(csv_file_path, conn):

    try:
        with open(csv_file_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            students_to_insert = [
                (
                    row['FirstName'],
                    row['LastName'],
                    row['Address'],
                    row['City'],
                    row['State'],
                    row['ZipCode'],
                    row['MobilePhoneNumber'],
                    row['Major'],
                    float(row['GPA']),
                    0  # Assuming isDeleted is 0 for new entries
                )
                for row in csv_reader
            ]
            cur = conn.cursor()
            cur.executemany('''
                INSERT INTO Students 
                (FirstName, LastName, Address, City, State, ZipCode, MobilePhoneNumber, Major, GPA, isDeleted) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', students_to_insert)
            conn.commit()
            print(f"Inserted {cur.rowcount} rows into Students table")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("CSV file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to display all students
def display_all_students(conn):
    """ Display all students and their attributes """
    cur = conn.cursor()
    query = "SELECT * FROM Students WHERE isDeleted=0"
    cur.execute(query)

    rows = cur.fetchall()
    for row in rows:
        print(row)


# Function to add a new student
def add_new_student(conn):
    try:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        major = input("Enter major: ")
        faculty_advisor = input("Enter faculty advisor: ")
        address = input("Enter address: ")
        city = input("Enter city: ")
        state = input("Enter state: ")
        zip_code = input("Enter zip code: ")
        mobile_phone_number = input("Enter mobile phone number: ")

        while True:  # wait for valid input
            gpa_input = input("Enter GPA: ")
            try:
                gpa = float(gpa_input)  # Attempt to convert input to a float
                if gpa < 0.0 or gpa > 4.0:  #real gpas only
                    print("GPA must be between 0.0 and 4.0")
                else:
                    break  # gpa is valid
            except ValueError:
                print("Invalid input for GPA. Please enter a numeric value.")  # retry

        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO Students 
                (FirstName, LastName, GPA, Major, FacultyAdvisor, Address, City, State, ZipCode, MobilePhoneNumber, isDeleted) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            first_name, last_name, gpa, major, faculty_advisor, address, city, state, zip_code, mobile_phone_number, 0))
            conn.commit()
            print("New student added successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")


# Function to update a student
def update_student(conn):
    # update student details
    student_id = input("Enter student ID to update: ")
    new_major = input("Enter new major (leave blank to not update): ")
    new_advisor = input("Enter new advisor (leave blank to not update): ")
    new_mobile_phone_number = input("Enter new mobile phone number (leave blank to not update): ")

    cur = conn.cursor()
    update_data = []
    query = "UPDATE Students SET "
    if new_major:
        query += "Major=?, "
        update_data.append(new_major)
    if new_advisor:
        query += "FacultyAdvisor=?, "
        update_data.append(new_advisor)
    if new_mobile_phone_number:
        query += "MobilePhoneNumber=?, "
        update_data.append(new_mobile_phone_number)

    # Remove extra comma and space
    query = query.rstrip(', ')
    query += " WHERE StudentId=? AND isDeleted=0"
    update_data.append(student_id)

    cur.execute(query, update_data)
    conn.commit()

    if cur.rowcount > 0:
        print("Student updated successfully.")
    else:
        print("No student found with the given ID, or the student is deleted.")


# delete student by StudentId function
def delete_student(conn):
    # set isDeleted to 1
    student_id = input("Enter student ID to delete: ")
    cur = conn.cursor()
    cur.execute("UPDATE Students SET isDeleted=1 WHERE StudentId=?", (student_id,))
    conn.commit()

    if cur.rowcount > 0:
        print("Student deleted successfully.")
    else:
        print("No student found with the given ID.")


# display students function
def search_students(conn):
    # Search students by major, GPA, city, state, and advisor
    search_query = input("Enter search query (Major, GPA, City, State, Advisor): ")
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM Students 
        WHERE (Major LIKE ? OR GPA LIKE ? OR City LIKE ? OR State LIKE ? OR FacultyAdvisor LIKE ?) 
        AND isDeleted=0
    ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%',
          '%' + search_query + '%'))

    rows = cur.fetchall()
    for row in rows:
        print(row)


def main():
    conn = create_connection(DATABASE_NAME)

    if conn is not None:
        create_table(conn)

        while True:
            print("\n--- Student Management System Menu ---")
            print("1. Display All Students")
            print("2. Add New Student")
            print("3. Update Student")
            print("4. Delete Student")
            print("5. Search Students")
            print("6. Import Students from CSV")
            print("7. Exit")

            choice = input("Enter the number of your choice: ")

            if choice == "1":
                display_all_students(conn)
            elif choice == "2":
                add_new_student(conn)
            elif choice == "3":
                update_student(conn)
            elif choice == "4":
                delete_student(conn)
            elif choice == "5":
                search_students(conn)
            elif choice == "6":
                import_from_students_csv(conn)
            elif choice == "7":
                print("Exiting the application.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
    else:
        print("Error! Cannot create the database connection.")

    if conn:  # Check if connection was successfully created
        conn.close()


if __name__ == '__main__':
    main()
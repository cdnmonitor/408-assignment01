import sqlite3
import csv
import os

DATABASE_NAME = "StudentDB.sqlite"


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
        cur.execute(
            """
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
        """
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def clean_phone_number(phone_number):
    # Remove any character that is not a digit or x for extension
    cleaned_number = "".join(
        filter(lambda x: x.isdigit() or x.lower() == "x", phone_number)
    )

    # Remove leading 1 if the length is greater than 10 after cleaning
    if len(cleaned_number) > 10 and cleaned_number.startswith("1"):
        cleaned_number = cleaned_number[1:]

    return cleaned_number


def import_from_students_csv(conn):
    csv_file_name = "students.csv"
    if os.path.isfile(csv_file_name):
        try:
            import_students_from_csv(csv_file_name, conn)
        except Exception as e:
            print(f"An error occurred while importing from CSV: {e}")
    else:
        print("The 'students.csv' file does not exist in the current directory.")


def import_students_from_csv(csv_file_path, conn):
    try:
        with open(csv_file_path, "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            students_to_insert = []
            for row in csv_reader:
                # clean the phone number before inserting
                cleaned_phone_number = clean_phone_number(row["MobilePhoneNumber"])

                students_to_insert.append(
                    (
                        row["FirstName"],
                        row["LastName"],
                        row["Address"],
                        row["City"],
                        row["State"],
                        row["ZipCode"],
                        cleaned_phone_number,  # cleaned and fixed phone number
                        row["Major"],
                        float(row["GPA"]),
                        0,  # isDeleted entry
                    )
                )

            cur = conn.cursor()
            cur.executemany(
                """
                INSERT INTO Students 
                (FirstName, LastName, Address, City, State, ZipCode, MobilePhoneNumber, Major, GPA, isDeleted) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                students_to_insert,
            )
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
    """Display all students and their attributes"""
    cur = conn.cursor()
    query = "SELECT * FROM Students WHERE isDeleted=0"
    cur.execute(query)

    rows = cur.fetchall()
    for row in rows:
        print(row)


# Helper function to get validated input
def get_validated_input(prompt_message, error_message, validation_function):
    while True:
        user_input = input(prompt_message).strip()
        if validation_function(user_input):
            return user_input
        else:
            print(error_message)


def is_valid_gpa(gpa):
    try:
        value = float(gpa)
        return 0.0 <= value <= 4.0
    except ValueError:
        return False


def is_valid_address(address):
    return len(address) <= 100


def is_valid_zip_code(zip_code):
    return zip_code.isdigit() and len(zip_code) == 5


def is_valid_phone_number(phone):
    return phone.isdigit() and len(phone) == 10


def is_valid_state(state):
    valid_states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    return state.upper() in valid_states


# Validation function for names allowing space
def is_valid_name(name):
    return all(x.isalpha() or x.isspace() for x in name) and len(name) <= 50


# Validation function for majors allowing letters, numbers, spaces, and some special characters
def is_valid_major(major):
    return (
        all(x.isalnum() or x.isspace() or x in "-&" for x in major) and len(major) <= 50
    )


# Function to add a new student with input validation and retry, not allowing blank entries
def add_new_student(conn):
    first_name = get_validated_input(
        "Enter first name: ",
        "Invalid first name. Must be alphabetic, non-empty, and less than 50 characters.",
        # if input is not an empty string and valid name function
        lambda input: input and is_valid_name(input),
    )
    last_name = get_validated_input(
        "Enter last name: ",
        "Invalid last name. Must be alphabetic, non-empty, and less than 50 characters.",
        lambda input: input and is_valid_name(input),
    )
    gpa = get_validated_input(
        "Enter GPA: ",
        "Invalid GPA. Must be a non-empty numeric value between 0.0 and 4.0.",
        lambda input: input and is_valid_gpa(input),
    )
    major = get_validated_input(
        "Enter major: ",
        "Invalid major. Must have char, letters, numbers, spaces, hyphens, and ampersands.",
        lambda input: input and is_valid_major(input),
    )
    address = get_validated_input(
        "Enter address: ",
        "Invalid address. Must be non-empty and less than 100 characters.",
        lambda input: input and is_valid_address(input),
    )
    city = get_validated_input(
        "Enter city: ",
        "Invalid city. Must be alphabetic, non-empty, and less than 50 characters.",
        lambda input: input and is_valid_name(input),
    )
    state = get_validated_input(
        "Enter state abbreviation (e.g., CA for California): ",
        "Invalid state abbreviation. Must be non-empty and a two-letter code such as 'CA'.",
        lambda input: input and is_valid_state(input),
    )
    zip_code = get_validated_input(
        "Enter zip code: ",
        "Invalid zip code. Must be non-empty and 5 digits.",
        lambda input: input and is_valid_zip_code(input),
    )
    mobile_phone_number = get_validated_input(
        "Enter mobile phone number: ",
        "Invalid phone number. Must be non-empty and 10 digits without any spaces or symbols.",
        lambda input: input and is_valid_phone_number(input),
    )

    # Convert GPA to float after validation
    gpa = float(gpa)

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Students 
            (FirstName, LastName, GPA, Major, Address, City, State, ZipCode, MobilePhoneNumber, isDeleted) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                first_name,
                last_name,
                gpa,
                major,
                address,
                city,
                state,
                zip_code,
                mobile_phone_number,
                0,
            ),
        )
        conn.commit()
        print("New student added successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Function to update a student
def update_student(conn):
    student_id = input("Enter student ID to update: ").strip()
    if not student_id.isdigit():
        print("Invalid student ID. Please enter a numeric value.")
        return

    cur = conn.cursor()

    # Check if student exists and is not deleted
    cur.execute("SELECT * FROM Students WHERE StudentId = ? AND isDeleted = 0", (student_id,))
    student = cur.fetchone()
    if not student:
        print("No student found with the given ID, or the student is deleted.")
        return

    print("Select an attribute to update:")
    attributes = {
        "1": "FirstName",
        "2": "LastName",
        "3": "GPA",
        "4": "Major",
        "5": "FacultyAdvisor",
        "6": "Address",
        "7": "City",
        "8": "State",
        "9": "ZipCode",
        "10": "MobilePhoneNumber",
    }
    for key, value in attributes.items():
        print(f"{key}. {value}")
    choice = input("Enter the number of the attribute: ")

    attribute = attributes.get(choice)
    if not attribute:
        print("Invalid choice.")
        return

    # Get the new value for the chosen attribute
    new_value = input(f"Enter the new value for {attribute}: ")

    # If the attribute is GPA, validate it's a float
    if attribute == "GPA" and not is_valid_gpa(new_value):
        print("Invalid GPA. Must be a numeric value between 0.0 and 4.0.")
        return

    # If the attribute is MobilePhoneNumber, validate it's a correct phone number
    if attribute == "MobilePhoneNumber" and not is_valid_phone_number(new_value):
        print("Invalid phone number. Must be 10 digits without any spaces or symbols.")
        return

    # Update the database
    update_query = f"UPDATE Students SET {attribute} = ? WHERE StudentId = ? AND isDeleted = 0"

    try:
        cur.execute(update_query, (new_value, student_id))
        conn.commit()
        if cur.rowcount > 0:
            print(f"Student {attribute} updated successfully to {new_value}.")
        else:
            print("No updates were made. Please check the student ID and try again.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


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


def search_students(conn):
    # choose an attribute to search by
    print("Select an attribute to search by:")
    print("1. First Name")
    print("2. Last Name")
    print("3. Major")
    print("4. City")
    print("5. State")
    print("6. GPA")
    print("7. Faculty Advisor")
    print("8. Mobile Phone Number")
    choice = input("Enter the number of the attribute: ")

    search_attributes = {
        "1": ("FirstName", is_valid_name),
        "2": ("LastName", is_valid_name),
        "3": ("Major", is_valid_major),
        "4": ("City", is_valid_name),
        "5": ("State", is_valid_state),
        "6": ("GPA", is_valid_gpa),
        "7": ("FacultyAdvisor", is_valid_name),
        "8": ("MobilePhoneNumber", is_valid_phone_number),
    }

    if choice not in search_attributes:
        print("Invalid choice. Please enter a number between 1 and 8.")
        return

    attribute, validation_function = search_attributes[choice]
    search_query = get_validated_input(
        f"Enter search query for {attribute}: ",
        f"Invalid input for {attribute}.",
        lambda input: input and validation_function(input)
    )

    cur = conn.cursor()

    if attribute == "GPA":
        # exact match instead of a LIKE query
        cur.execute(f"SELECT * FROM Students WHERE {attribute} = ? AND isDeleted = 0", (search_query,))
    else:
        # LIKE for a simple pattern match
        cur.execute(f"SELECT * FROM Students WHERE {attribute} LIKE ? AND isDeleted = 0", (f"%{search_query}%",))

    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print(f"No results found for {search_query} in {attribute}.")


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
                print("Exiting.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
    else:
        print("Error! Cannot create the database connection.")

    if conn:  # close in case
        conn.close()


if __name__ == "__main__":
    main()

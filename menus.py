from auth import signup, login

def main_menu():
    while True:
        print("\n====================")
        print("STUDENT GRADE TRACKER")
        print("====================")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Good Bye")
            break
        else:
            print("Invalid Choice.")

# Refactored: Standardized terminal color margins and menu alignments.

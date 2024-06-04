from collections import UserDict
from datetime import datetime, date
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if self.validate_phone(value):
             super().__init__(value)
        else: 
            raise ValueError('Phone number should contain 10 digits.')
    
    @staticmethod
    def validate_phone(value):
         return value.isdigit() and len(value) == 10
             
        
class Birthday(Field):
    def __init__(self, value):
        try:
             self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
             

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"
    
    def add_phone(self, phone):
         self.phones.append(Phone(phone))

    def remove_phone(self, phone):
         self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        try:
            Phone(new_phone)
        except ValueError as e:
            return str(e)
        
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return f'Phone number has changed from {old_phone} to {new_phone} for {self.name.value}'
        return f'Phone number {old_phone} not found for {self.name.value}'
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
                 
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

class AddressBook(UserDict):
    
     def add_record(self, record):
          self.data[record.name.value] = record
     
     def find(self, name: str) -> Record:
            return self.data.get(name, None)
     
     def delete(self, name:str):
        if name in self.data:
            del self.data[name]

     def get_upcoming_birthdays(self, days=7):
       upcoming_birthdays = []
       today = date.today()
       for record in self.data.values():
        if record.birthday:
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

        if 0 <= (birthday_this_year - today).days <= days:
            upcoming_birthdays.append({
                "name": record.name.value, 
                "congratulation_date": birthday_this_year.strftime('%d.%m.%Y')
                })
       return upcoming_birthdays

def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "No such contact found. Please try again."
        except ValueError as e:
            return str(e)
        except IndexError:
            return " Command format is incorrect."
    return inner

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

@input_error
def add_contact(args, book: "AddressBook"):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    if phone:
        record.add_phone(phone)
        message += f" Phone number {phone} added."
    return message

@input_error  
def change_contact(args, book: "AddressBook"):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return f"New contact number {phone} is updated."
    else:
        return f"No name {name} is found in contacts."
    

@input_error
def show_phone(args,book: "AddressBook"):
    name = args[0]
    record = book.find(name)
    if record:
        return f"The phone number for '{name}' is {', '.join(p.value for p in record.phones)}"
    else:
        return f"No name '{name}' is found in contacts."
    
@input_error
def show_all(book: "AddressBook"):
    if book.data:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "No contacts."
    
@input_error
def add_birthday(args, book):
    name, date_str = args
    record = book.find(name)
    if not record:
        return f'No contact found'
    try:
        record.add_birthday(date_str)
        return f'Birthday for {name}:{date_str} added'
    except ValueError as e:
        return str(e)
    
@input_error
def show_birthday(args, book):
         name = args[0]
         record = book.find(name)
         if not record:
             return f'No contact found'
         if record.birthday:
             return f'{name}´s birday is {record.birthday.value.strftime("%d.%m.%Y")}'
         else:
             return f'{name} bithday was not found'

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return f'No upcoming birthdays'
    
    result = ['Upcoming birthdays in the next week:']
    for record in upcoming_birthdays:
        name = record['name']
        birthday = record['congratulation_date']
        result.append(f'{name}: {birthday}')
    return "\n".join(result)
    
    
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("Please enter a command.")
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == 'add-birthday':
            print(add_birthday(args, book))
        elif command == 'show-birthday':
            print(show_birthday(args, book))
        elif command == 'birthdays':
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")

book.add_record(john_record)


jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

for name, record in book.data.items():
    print(record)


john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john) 


found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("Jane")
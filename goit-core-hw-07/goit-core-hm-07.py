from collections import UserDict
import re
from datetime import datetime, date

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
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return " Command format is incorrect."
    return inner

@input_error
def add_contact(args, book: "AddressBook"):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
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
        return f"The phone number for '{name}' is {record.phones}"
    else:
        return f"No name '{name}' is found in contacts."
    

@input_error
def show_all(book: "AddressBook"):
    if book.data:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "No contacts."
    
    
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
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
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self.validate_phone(value)
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError('Phone number must be 10 digits')
             
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.birthday = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
             

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self, phone):
          if not isinstance(phone,Phone):
               raise ValueError("Please correct the phone number")
          self.phones.append(phone)

    def remove_phone(self, phone):
        if not isinstance(phone, Phone):
             raise ValueError("Please correct the phone number")
        self.phones.remove(phone)

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
    
                 
    def find_phone(self, phone: Phone):
        matching_phones = list(filter(lambda p: p.value == phone.value, self.phones ))
        return matching_phones[0] if matching_phones else None
    
    def add_birthday(self, birthday):
          if not isinstance(birthday, Birthday):
              raise ValueError("Please enter the correct birthday")
          if self.birthday is None:
              self.birthday = []
          self.birthday.append(birthday)

    def valid_birthday(self, birthday: Phone):
       return birthday in self.birthday

class AddressBook(UserDict):
    
     def add_record(self, record):
           if not isinstance(record, Record):
                raise ValueError()
           self.data[record.name.value] = record
     
     def find(self, name: str) -> Record:
            return self.data.get(name)
     
     def delete(self, name:str):
              if name in self.data:
                   del self.data[name]

     def get_upcoming_birthdays(self, days=7):
       upcoming_birthdays = []
       today = date.today()
       for record in self.data.values():
        if record.birthday:
            birthday_this_year = record.birthday.replace(year=today.year)
        
        if birthday_this_year.date < today:
            birthday_this_year = birthday_this_year.value.replace(year=today.year + 1)
        
        birthday_this_year = self.adjust_for_weekend(birthday_this_year)
        if 0 <= (birthday_this_year.date() - today).days <= days:
            congratulation_date_str = self.date_to_string(birthday_this_year)
            upcoming_birthdays.append({
                "name": record.name, 
                "congratulation_date": congratulation_date_str
                })
       return upcoming_birthdays
     
     @input_error
     def add_birthday(args, book):
         name, date_str = args
         record = book.get(name)
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
             return f'{name}´s birday is {record.birthday}'
         else:
             return f'{name} bithday was not found'

     @input_error
     def birthdays(args, book):
         upcoming_birthdays = book.get_upcoming_birthdays()
         if not upcoming_birthdays:
             return f'No upcoming birthdays'
         result = "Upcoming birthdays in the next week:\n"
         return result
     
    

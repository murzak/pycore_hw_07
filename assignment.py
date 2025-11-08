import re
from collections import UserDict
from datetime import datetime, timedelta

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return 'Not enough arguments'
        except KeyError:
            return 'Contact not found'
    return wrapper


def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

class Field:
    # Base class for fields like Name and Phone
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # Represents a contact name
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    # Represents a phone number
    PH_PATTERN = re.compile(r'^\d{10}$')

    def __init__(self, value):
        if not self.PH_PATTERN.match(value):
            raise ValueError('Phone number must contain exactly 10 digits.')
        super().__init__(value)

    def __eq__(self, other):
        # Checks for equality of instances in case of equal values
        if not isinstance(other, Phone):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        # Now are able to be added in lists
        return hash(self.value)
    

class Birthday(Field):
    BD_PATTERN = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
    def __init__(self, value):
        if not re.match(self.BD_PATTERN, value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            if re.match(self.BD_PATTERN, value):
                self.value = datetime.strptime(value.strip(), "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    # Represents a contact record containing a name and multiple phone numbers
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        # Adds a new phone number if valid and not duplicated
        phone_obj = Phone(phone)
        if phone_obj not in self.phones:
            self.phones.append(phone_obj)
        else:
            raise ValueError('This phone number already exists')
        
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday

    def find_phone(self, phone):
        # Searches for a phone in the record
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError('Phone number not found')

    def edit_phone(self, old, new):
        # Phone validation is done in Phone class
        phone_old = self.find_phone(old)
        phone_new = Phone(new)
        idx = self.phones.index(phone_old)
        self.phones[idx] = phone_new
        

    def delete_phone(self, phone):
        # Deletes a phone number from the record
        phone_obj = self.find_phone(phone)
        self.phones.remove(phone_obj)

    def __str__(self):
        # Returns formatted string representation of the record
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    

class AddressBook(UserDict):
    def add_record(self, record):
        # Adds a contact record indexed by contact name
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
    # Initiate an empty output array
        birthday_users = []

        # Loop through users
        for record in self.data.values():

            # Concatenate this or next year with string pattern DD.MM to get 2 possible birthdays
            birthday = record.birthday.value.strftime("%d.%m.%Y")
            ddmm = '.'.join(birthday.split('.')[:-1])
            this_year = datetime.today().year
            next_year = this_year + 1

            # For each year loop through and calculate difference in days 
            for year in [this_year, next_year]:
                birthday = f'{ddmm}.{year}'
                birthday_dt = datetime.strptime(birthday, '%d.%m.%Y').date()
                days_diff = (birthday_dt - datetime.today().date()).days

                # In case difference between 0 and 7, inclusively. 
                # Return congratulation date as birthday itself in case it happens Monday through Friday, otherwise, move to the next Monday
                if 0 <= days_diff <= 7:
                    if 0 <= birthday_dt.weekday() <= 4:
                        birthday_users.append({'name': record.name.value, 
                                               'congratulation_date': birthday})
                    else:
                        birthday_users.append({'name': record.name.value, 
                                               'congratulation_date': datetime.strftime(birthday_dt + timedelta(days=7-birthday_dt.weekday()), '%d.%m.%Y')})
        return birthday_users

    def find(self, name):
        # Finds a record by name
        # print(self.data.values())
        return self.data.get(name)

    def delete(self, name):
        # Deletes a record by name
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError('This name does not exist in this address book')


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = 'Contact added.'
    else:
        message = 'Contact updated.'
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, phone_old, phone_new = args
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    else:
        record.edit_phone(phone_old, phone_new)
        message = 'Contact updated'
    return message

@input_error   
def delete_contact(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    book.delete(name)
    return 'Contact deleted'


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    return ('; '.join(p.value for p in record.phones)).strip()

@input_error
def show_all(book):
    output = []
    if book.data.values():
        for record in book.data.values():
            output.append(str(record))
        return '\n'.join(output)
    return 'No contacts found'
    
@input_error
def delete_phone(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    # print(record.phones)
    if phone not in [p.value for p in record.phones]:
        raise ValueError('No such phone number in contact')
    record.delete_phone(phone)
    return 'Phone deleted'

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    if record.birthday:
        raise ValueError('Birthday already given')
    record.add_birthday(birthday)
    return 'Birthday added'

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise ValueError('No contact found')
    if record and not record.birthday:
        raise ValueError('No birthday found')
    return record.birthday.value.strftime("%d.%m.%Y")

@input_error
def birthdays(book):
    result = book.get_upcoming_birthdays()
    return '\n'.join([str(bd_user) for bd_user in result]) if result else 'No upcoming birthdays available'


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == 'delete':
            print(delete_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == 'delete-phone':
            print(delete_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


main()
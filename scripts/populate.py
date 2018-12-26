from app.operations import User, Command
import random, string, hashlib
import argparse, getpass, re
import subprocess

# WIP Commandline Management

def ask_details():
    userdetails = dict.fromkeys(['password', 'email'])
    while userdetails['password'] is None:
        userdetails['password'] = getpass.getpass()

    while userdetails['email'] is None:
        emailUnparsed = input("Email: ")
        regexMail = re.search(
            "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            emailUnparsed)
        if regexMail:
            userdetails['email'] = emailUnparsed
        else:
            print("Invalid email format")

    return userdetails


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="The username to perform the action on", required=False)
    parser.add_argument("-a", "--action", help="Action to perform: delete||add", required=True)
    parser.add_argument("-c", "--command", help="Command name to add", required=False)
    parser.add_argument("-t", "--type", help="Type of command", required=False)
    args = parser.parse_args()

    if args.action == "create":
        if args.user:
            userdetails = ask_details()
            print(User().create(args.user, userdetails['password'], userdetails['email'], "administrator"))
        if args.command and args.type:
            print(Command.create(args.command, args.type))

    else:
        print("Invalid options. Either supply add (-c or -u), delete (-c or -u), fill or delete_database as actions")

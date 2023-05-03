#!/usr/bin/python3
# import necessary modules
import re
import subprocess
import smtplib
import socket
import datetime
import time
import configparser
import ipaddress
import os

# import config
config = configparser.ConfigParser()
config.read("/etc/sshwatch")
HOSTNAME = config["DEFAULT"]["HOSTNAME"]
LOG_READ = config["LOGGING"]["LOG_READ"]
LOG_WRITE = config["LOGGING"]["LOG_WRITE"]
RECEIVER = config["MAIL"]["RECEIVER"]
SUBJECT = config["MAIL"]["SUBJECT"]
BODY = config["MAIL"]["BODY"]
LOGIN_PASSWORD = config["PATTERN"]["LOGIN_PASSWORD"]
LOGIN_PUBLICKEY = config["PATTERN"]["LOGIN_PUBLICKEY"]
DISCONNECT_PATTERN = config["PATTERN"]["DISCONNECT_PATTERN"]
# Helper function to send an email alert


def send_email(BODY, SUBJECT):
    try:
        os.system("echo '{}' | mail -s '{}' '{}'".format(BODY, SUBJECT, RECEIVER))
        print("Email sent")
    except Exception as e:
        print("Error sending email:", e)


# Helper function to get geolocip


def get_location(ip_from):
    if ipaddress.ip_address(ip_from).is_private:
        return "Private IP address"
    try:
        location = subprocess.check_output(
            ["geoiplookup", ip_address]).decode().strip()
    except FileNotFoundError:
        location = "Unknown"
    return location


# Continuously read the auth.log file and detect events
with subprocess.Popen(
    ["tail", "-F", LOG_READ], stdout=subprocess.PIPE, stderr=subprocess.PIPE
) as proc:
    while True:
        # Read the next line from the auth.log file

        line = proc.stdout.readline().decode("utf-8").strip()
        if not line:
            time.sleep(0.1)
            continue
            # Check if the line matches the login or disconnect pattern

        password_login = re.search(LOGIN_PASSWORD, line)
        publkey_login = re.search(LOGIN_PUBLICKEY, line)
        disconnect_match = re.match(DISCONNECT_PATTERN, line)
        if publkey_login:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = publkey_login.group(1)
            ip_from = publkey_login.group(2)
            ssh_key = publkey_login.group(3)
            location = get_location(ip_from)
            message = f"{date} : New login detected for {username} from {ip_from} ({location}) with {ssh_key}"
            with open("LOG_WRITE", "a") as f:
                f.write(message + "\n")
            send_email(BODY, SUBJECT)
        elif password_login:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = password_login.group(1)
            ip_from = password_login.group(2)
            location = get_location(ip_from)
            message = f"{date} : New login detected for {username} from {ip_from} ({location})"
            with open("LOG_WRITE", "a") as f:
                f.write(message + "\n")
            send_email(BODY, SUBJECT)
        elif disconnect_match:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            host = disconnect_match.group(1)
            username = disconnect_match.group(2)
            message = f"{date} : {username} disconnected from {host}"
            with open("LOG_WRITE", "a") as f:
                f.write(message + "\n")
        else:
            continue

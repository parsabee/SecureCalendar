# Calendar event data encryption module
# Used with the pycryptodome module
# Code derive from pycryptodome website manual page:
# https://www.pycryptodome.org/en/latest/src/cipher/chacha20.html

from Cryptodome.Cipher import ChaCha20  # The encryption cipher for secure cal.
from io import StringIO  # For string conversion.
import csv  # For convenient reading of csv files.
import os  # For operating specific newline char.
from Cryptodome.Hash import SHA256

def encrypt_and_store(username, password, string):
    # Encrypts given string with password key and writes encrypted data to username.csv
    h = SHA256.new(data = password.encode())##Generate a SHA256 hash using password
    k = h.digest()
    cipher = ChaCha20.new(key=k)
    msg = cipher.nonce + cipher.encrypt(string.encode())  # Generate the encrypted string.
    with open(username + '.cal', 'wb') as f:  # write encrypted data to a file. Overwrites existing file.
        f.write(msg)


def decrypt_and_get_list(username, password):
    # Opens username.cal and returns decrypted string. Returns -1 on failure.
    with open(username + ".cal", "rb") as f:
        msg = f.read()  # Read the file.
    msg_nonce = msg[:8]  # Seperate the file into the nonce and text.
    ciphertext = msg[8:]
    key = password.ljust(32)
    h = SHA256.new(data = password.encode())#Generate a SHA256 hash using password
    k = h.digest()
    cipher = ChaCha20.new(key=k, nonce=msg_nonce)  # Specify the chacha20 cipher.
    try:
        # Decode the text.
        data = cipher.decrypt(ciphertext).decode()
    except UnicodeDecodeError:
        return -1

    f = StringIO(data)  # Read through the contents of the data string as if it were a file.
    if f.readline() != "Title\tStart\tEnd\tLocation\tDescription\tNotes" + os.linesep:
        return -1  # If the first line is not the expected header, then file is bad.
    # Create a list from the lines in the tsv file after the first line, then return the list.
    event_list = list(csv.reader(f, delimiter='\t'))
    return event_list

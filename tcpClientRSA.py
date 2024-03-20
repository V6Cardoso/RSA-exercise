from socket import *
import random
import ast
import struct

def miller_rabin(num, k=2):
    if num == 2 or num == 3:
        return True

    if num % 2 == 0:
        return False

    exponent, odd_part = 0, num - 1
    while odd_part % 2 == 0:
        exponent += 1
        odd_part //= 2

    for _ in range(k):
        witness = random.randrange(2, num - 1)
        x = pow(witness, odd_part, num)

        if x == 1 or x == num - 1:
            continue

        for _ in range(exponent - 1):
            x = pow(x, 2, num)
            if x == num - 1:
                break
        else:
            return False

    return True

def generate_large_prime(n_bits):
    while True:
        p = random.getrandbits(n_bits)
        if miller_rabin(p):
            return p
        
def generate_primes(n_bits):
    prime_candidate = generate_large_prime(n_bits)
    print("Prime: ", prime_candidate, "\n")

    prime_candidate2 = 0
    while True:
        prime_candidate2 = generate_large_prime(n_bits)
        if prime_candidate2 != prime_candidate:
            break

    print("Prime2: ", prime_candidate2, "\n")
    return prime_candidate, prime_candidate2


def coprime_integers(num1, num2):
    def gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a

    return gcd(num1, num2) == 1

def generate_e(phi):
    e = 0
    while True:
        e = random.randrange(1, phi)
        if coprime_integers(e, phi):
            break

    return e

def multiplicative_inverse(e, phi):
        def extended_gcd(a, b):
            x, y, u, v = 0, 1, 1, 0
            while a != 0:
                q, r = b // a, b % a
                m, n = x - u * q, y - v * q
                b, a, x, y, u, v = a, r, u, v, m, n
            return b, x, y

        g, x, _ = extended_gcd(e, phi)
        if g == 1:
            return x % phi

def generate_keys(n_bits=1024):
    prime_candidate, prime_candidate2 = generate_primes(n_bits)

    N = prime_candidate * prime_candidate2
    print("N: ", N, "\n")

    phi = (prime_candidate - 1) * (prime_candidate2 - 1)
    print("Phi: ", phi, "\n")

    e = generate_e(phi)
    print("e: ", e, "\n")

    d = multiplicative_inverse(e, phi)
    print("d: ", d, "\n")

    return (e, N), (d, N)

def encrypt(message, e, N):
    cipher = [pow(ord(char), e, N) for char in message]
    return cipher

def decrypt(cipher, d, N):
    message = [chr(pow(char, d, N)) for char in cipher]
    return ''.join(message)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


serverName = "192.168.15.21" # Put the server IP address here
serverPort = 1300
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.settimeout(3600)
clientSocket.connect((serverName,serverPort))

data_length = recvall(clientSocket, 4)
data_length = struct.unpack(">I", data_length)[0]


# Wait for the server to send the public key (e, N)
data = recvall(clientSocket, data_length)
server_public_key = ast.literal_eval(data.decode("utf-8"))
print("Received from Make Upper Case Server: ", server_public_key)
server_e, server_N = server_public_key


sentence = input("Input lowercase sentence: ")
sentence = sentence.lower()
cryptographSentence = encrypt(sentence, server_e, server_N)

# Send the encrypted message to the server
cryptographSentence_bytes = bytes(str(cryptographSentence), "utf-8")
cryptographSentence_length = len(cryptographSentence_bytes)

cryptographSentence_length_packed = struct.pack('>I', cryptographSentence_length)

print("Sending bytes:", cryptographSentence_bytes)

clientSocket.send(cryptographSentence_length_packed + cryptographSentence_bytes)

# Generate pair of keys
public_key, private_key = generate_keys(4096)
private_d, private_N = private_key

# Convert the public key to bytes
public_key_bytes = bytes(str(public_key), "utf-8")

# Get the length of the public key bytes
public_key_length = len(public_key_bytes)

# Pack the length into a 4-byte big endian integer
public_key_length_packed = struct.pack('>I', public_key_length)

# Send the length of the public key followed by the public key itself
clientSocket.send(public_key_length_packed + public_key_bytes)

# Wait for the server to send the encrypted message
data_length = recvall(clientSocket, 4)
data_length = struct.unpack(">I", data_length)[0]
received_message = recvall(clientSocket, data_length)
print ("Received from Make Upper Case Server: ", received_message)
decryptText = decrypt(ast.literal_eval(received_message.decode("utf-8")), private_d, private_N)

print ("Received from Make Upper Case Server: ", decryptText)
clientSocket.close()
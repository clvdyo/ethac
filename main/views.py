import random
from django.shortcuts import render
from django.http import JsonResponse
from django import forms

# Helper Functions
def checkPrimeFermat(p):
    assert p > 2 and p % 2 == 1
    numberOfTrials = len(str(p)) * 3
    for _ in range(numberOfTrials):
        a = random.randint(2, p - 1)
        if pow(a, p - 1, p) != 1:
            return False
    return True

def isBlumInteger(p, q):
    return p % 4 == 3 and q % 4 == 3

def generateTwoPrime(bit_length):
    prime_list = []
    lower_bound = 2 ** (bit_length - 1)
    upper_bound = 2 ** bit_length - 1

    while len(prime_list) < 2:
        candidate = random.randint(lower_bound, upper_bound) | 1
        if checkPrimeFermat(candidate) and candidate not in prime_list:
            prime_list.append(candidate)

    p, q = prime_list
    if isBlumInteger(p, q):
        n = p * q
        return p, q, n
    else:
        return generateTwoPrime(bit_length)

def encrypt_message(message, n):
    results = []
    for char in message:
        ascii_value = ord(char)
        binary_value = bin(ascii_value)[2:]
        double_binary_value = binary_value + binary_value
        m = int(double_binary_value, 2)
        c = pow(m, 2, n)
        results.append((char, m, c))
    return results

# Django Form untuk input data
class InputForm(forms.Form):
    bit_length = forms.IntegerField(label="Digit Panjang Bit (Contoh: 15)", min_value=2)
    message = forms.CharField(label="Pesan untuk Enkripsi", max_length=255)

def index(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            bit_length = form.cleaned_data['bit_length']
            message = form.cleaned_data['message']

            # Generate keys
            p, q, n = generateTwoPrime(bit_length)

            # Encrypt message
            encrypted_results = encrypt_message(message, n)

            return JsonResponse({
                "private_key": {"p": p, "q": q},
                "public_key": {"n": n},
                "encrypted_message": [{
                    "character": char,
                    "m": m,
                    "ciphertext": c
                } for char, m, c in encrypted_results]
            })

    else:
        form = InputForm()

    return render(request, "index.html", {"form": form})


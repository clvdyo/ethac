import random
import math
from django.shortcuts import render
from django.http import JsonResponse
from django import forms
from django.shortcuts import redirect

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

def brute_force(n):
    for p in range(3, int(math.sqrt(n)) + 1, 2):
        if n % p == 0:
            q = n // p
            return p, q
    return None, None

# Django Form untuk input data
class EncryptionForm(forms.Form):
    bit_length = forms.IntegerField(label="Digit Panjang Bit (Contoh: 15)", min_value=2)
    message = forms.CharField(label="Pesan untuk Enkripsi", max_length=255)
    
class BruteForceForm(forms.Form):
    n = forms.IntegerField(label="Masukkan nilai n", min_value=2)

def index(request):
    # Inisialisasi form
    encryption_form = EncryptionForm(prefix="encryption")
    brute_force_form = BruteForceForm(prefix="brute")

    # Hasil proses form
    encryption_result = request.session.get('encryption_result', None)
    brute_force_result = None

    if request.method == "POST":
        if "encryption_submit" in request.POST:
            encryption_form = EncryptionForm(request.POST, prefix="encryption")
            if encryption_form.is_valid():
                bit_length = encryption_form.cleaned_data['bit_length']
                message = encryption_form.cleaned_data['message']

                # Generate keys dan hasil enkripsi
                p, q, n = generateTwoPrime(bit_length)
                encrypted_message = encrypt_message(message, n)

                encryption_result = {
                    "private_key": {"p": p, "q": q},
                    "public_key": {"n": n},
                    "encrypted_message": encrypted_message
                }
                
                request.session['encryption_result'] = encryption_result

        elif "brute_force_submit" in request.POST:
            brute_force_form = BruteForceForm(request.POST, prefix="brute")
            if brute_force_form.is_valid():
                n = brute_force_form.cleaned_data['n']
                p, q = brute_force(n)

                brute_force_result = {
                    "p": p, 
                    "q": q
                } if p and q else {"error": "Tidak dapat menemukan faktor p dan q."}

    # Render halaman dengan hasil form
    return render(request, 'index.html', {
        'encryption_form': encryption_form,
        'brute_force_form': brute_force_form,
        'encryption_result': encryption_result,
        'brute_force_result': brute_force_result
    })
import random
import math
from django.shortcuts import render
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

def extendedEuclidean(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extendedEuclidean(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

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

def decrypt_message(ciphertexts, p, q, n):
    gcd, yp, yq = extendedEuclidean(p, q)

    decrypted_results = []
    for c in ciphertexts:
        mp = pow(c, (p + 1) // 4, p)
        mq = pow(c, (q + 1) // 4, q)

        v = yp * p * mq
        w = yq * q * mp

        r = (v + w) % n
        s = (v - w) % n
        t = (-v + w) % n
        u = (-v - w) % n

        decrypted_results.extend([r, s, t, u])

    symmetric_results = []
    for value in decrypted_results:
        binary_str = bin(value)[2:]
        half_len = len(binary_str) // 2
        if binary_str[:half_len] == binary_str[half_len:]:
            symmetric_results.append(int(binary_str[:half_len], 2))

    decrypted_message = ''.join(chr(value) for value in symmetric_results)
    return decrypted_message

def brute_force(n):
    for p in range(3, int(math.sqrt(n)) + 1, 2):
        if n % p == 0:
            q = n // p
            return p, q
    return None, None

# Django Forms
class EncryptionForm(forms.Form):
    bit_length = forms.IntegerField(label="Digit Panjang Bit (Contoh: 15)", min_value=8)
    message = forms.CharField(label="Pesan untuk Enkripsi", max_length=255)

class BruteForceForm(forms.Form):
    n = forms.IntegerField(label="Masukkan nilai n", min_value=77)

def index(request):
    encryption_form = EncryptionForm(prefix="encryption")
    brute_force_form = BruteForceForm(prefix="brute")

    encryption_result = request.session.get('encryption_result', None)
    decryption_result = request.session.get('decryption_result', None)
    brute_force_result = None

    if request.method == "POST":
        if "encryption_submit" in request.POST:
            # Proses Enkripsi
            encryption_form = EncryptionForm(request.POST, prefix="encryption")
            if encryption_form.is_valid():
                bit_length = encryption_form.cleaned_data['bit_length']
                message = encryption_form.cleaned_data['message']

                # Generate kunci dan enkripsi pesan
                p, q, n = generateTwoPrime(bit_length)
                encrypted_message = encrypt_message(message, n)

                encryption_result = {
                    "private_key": {"p": p, "q": q},
                    "public_key": {"n": n},
                    "encrypted_message": encrypted_message,
                }
                request.session['encryption_result'] = encryption_result

        elif "decryption_submit" in request.POST:
            # Proses Dekripsi
            p = request.POST.get("p")
            q = request.POST.get("q")
            n = request.POST.get("n")
            encrypted_message_raw = request.POST.get("encrypted_message")

            if not all([p, q, n, encrypted_message_raw]):
                decryption_result = {"error": "Semua field harus diisi!"}
            else:
                try:
                    # Konversi nilai
                    p = int(p)
                    q = int(q)
                    n = int(n)
                    ciphertexts = [int(c) for c in encrypted_message_raw.split(",")]

                    # Dekripsi pesan
                    decrypted_message = decrypt_message(ciphertexts, p, q, n)

                    decryption_result = {
                        "original_message": decrypted_message,
                        "details": ciphertexts,
                    }
                    request.session['decryption_result'] = decryption_result
                except ValueError:
                    decryption_result = {"error": "Masukkan angka yang valid untuk p, q, n, dan ciphertext!"}
                except Exception as e:
                    decryption_result = {"error": f"Terjadi kesalahan selama dekripsi: {str(e)}"}

        elif "brute_force_submit" in request.POST:
            # Proses Brute Force
            brute_force_form = BruteForceForm(request.POST, prefix="brute")
            if brute_force_form.is_valid():
                n = brute_force_form.cleaned_data['n']
                p, q = brute_force(n)

                brute_force_result = {
                    "p": p,
                    "q": q,
                } if p and q else {"error": "Tidak dapat menemukan faktor p dan q."}

    return render(request, 'index.html', {
        'encryption_form': encryption_form,
        'brute_force_form': brute_force_form,
        'encryption_result': encryption_result,
        'decryption_result': decryption_result,
        'brute_force_result': brute_force_result,
    })

from django.shortcuts import render
import random

def checkPrimeFermat(p):
    assert p > 2 and p % 2 == 1
    numberOfTrials = len(str(p)) * 3
    for i in range(numberOfTrials):
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

def keygeneration(request):
    p, q, n = None, None, None  # Initial values

    if request.method == "POST":
        # Get the bit length from the form
        bit_length = int(request.POST.get("bit_length"))
        
        # Generate the two primes and n
        p, q, n = generateTwoPrime(bit_length)

    return render(request, 'base/keygeneration.html', {'p': p, 'q': q, 'n': n})

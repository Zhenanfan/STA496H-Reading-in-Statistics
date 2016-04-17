import binascii
from string import maketrans
import random
import numpy as np
import operator

def update_bigram(text,bigram):
    for i in range(0, len(text)):
        temp = text[i:i+2]
        bigram[temp] = bigram.get(temp,0) + 1
    return bigram

def update_unigram(text,unigram):
    for i in range(len(text)):
        temp = text[i]
        unigram[temp] = unigram.get(temp,0) + 1
    return unigram

def encrypt_substitution(text, key):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '
    translation = maketrans(alphabet, key)
    return text.translate(translation)
    


def logpi(ciphertext,bigram_reference):
    bigram_reference.pop("\n", None)
    bigram_reference.pop(" \n", None)
##    text1 = encrypt_substitution(text, key_s)
##    textlength = len(plaintext)
##    keylength = len(key_t)
##    ciphertext = encrypt_transposition(plaintext,textlength,key_t,keylength)
    bigram_train = dict()
    for i in range(len(ciphertext)):
        temp = ciphertext[i:i+2]
        bigram_train[temp] = bigram_train.get(temp,0) + 1
    l = 0
    for beta in bigram_train.keys():
    	l = l + (bigram_train[beta]+1)*np.log(bigram_reference.get(beta,0)+1)
    return l


def swap(testkey_substitution):
    i,j = np.random.randint(27,size = 2)
    l = list(testkey_substitution)
    l[i],l[j] = l[j],l[i]
    return ''.join(l)

def decrypt_unigram(ciphertext, unigram_reference):
    unigram_reference.pop("\n", None)
    unigram_reference.pop(" ", None)
    unigram_cipher = dict()
    for i in range(len(ciphertext)):
        temp = ciphertext[i]
        if not temp == ' ':
            unigram_cipher[temp] = unigram_cipher.get(temp,0) + 1
    sorted_reference = sorted(unigram_reference.items(), key=operator.itemgetter(1))
    sorted_cipher = sorted(unigram_cipher.items(), key=operator.itemgetter(1))
    char_reference = []
    char_cipher = []
    for i in range(len(sorted_cipher)):
        char_reference.append(sorted_reference[i][0])
        char_cipher.append(sorted_cipher[i][0])
    alphabet = ''.join(char_cipher)
    key = ''.join(char_reference)
    translation = maketrans(alphabet, key)
    return ciphertext.translate(translation)
    



def decrypt_substitution(ciphertext,bigram_reference):
    M = 3000
    textlength = len(ciphertext)
    x = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '
    xlist = []
    xlist.append(x)
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    for i in range(M):
        tau = 3.0/(i+1)
        p = 1.0/tau
        y = swap(x)
        u = np.random.uniform(0,1)
        ciphertext2 = encrypt_substitution(ciphertext, y)
        score_new = logpi(ciphertext2,bigram_reference)
        alpha = p*(score_new - scorelist[i])
        if np.log(u) < alpha :
            x = y
            naccept = naccept + 1
            scorelist.append(score_new)
        else:
            scorelist.append(scorelist[i])
        xlist.append(x)
    index = scorelist.index(max(scorelist))
    return [xlist[index],naccept,max(scorelist),index]


def permutate(original, fixed_key):
    return ''.join(original[i - 1] for i in fixed_key)


def left_half(bits):
    return bits[:len(bits)//2]


def right_half(bits):
    return bits[len(bits)//2:]


def shift(bits):
    rotated_left_half = left_half(bits)[1:] + left_half(bits)[0]
    rotated_right_half = right_half(bits)[1:] + right_half(bits)[0]
    return rotated_left_half + rotated_right_half


def key1():
##    return permutate(shift(permutate(KEY, FIXED_P10)), FIXED_P8)
    return '10100100'

def key2():
##    return permutate(shift(shift(shift(permutate(KEY, FIXED_P10)))), FIXED_P8)
    return '01000011'

def xor(bits, key):
    return ''.join(str(((bit + key_bit) % 2)) for bit, key_bit in
                   zip(map(int, bits), map(int, key)))


def lookup_in_sbox(bits, sbox):
    row = int(bits[0] + bits[3], 2)
    col = int(bits[1] + bits[2], 2)
    return '{0:02b}'.format(sbox[row][col])


def f_k(bits, key):
    L = left_half(bits)
    R = right_half(bits)
    bits = permutate(R, FIXED_EP)
    bits = xor(bits, key)
    bits = lookup_in_sbox(left_half(bits), S0) + lookup_in_sbox(right_half(bits), S1)
    bits = permutate(bits, FIXED_P4)
    return xor(bits, L)


def encrypt_sdes(plain_text):
    bits = permutate(plain_text, FIXED_IP)
    temp = f_k(bits, key1())
    bits = right_half(bits) + temp
    bits = f_k(bits, key2())
    return permutate(bits + temp, FIXED_IP_INVERSE)


##def decrypt(cipher_text):
##    bits = permutate(cipher_text, FIXED_IP)
##    temp = f_k(bits, key2())
##    bits = right_half(bits) + temp
##    bits = f_k(bits, key1())
##    print permutate(bits + temp, FIXED_IP_INVERSE)

def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))



if __name__ == '__main__':
    bigram_reference = dict()
    unigram_reference = dict()

    with open('warorig') as f:
        for line in f:
           bigram_reference = update_bigram(line,bigram_reference)
           unigram_reference = update_unigram(line,unigram_reference)

    
    FIXED_IP = [2, 6, 3, 1, 4, 8, 5, 7]
    FIXED_EP = [4, 1, 2, 3, 2, 3, 4, 1]
    FIXED_IP_INVERSE = [4, 1, 3, 5, 7, 2, 8, 6]
    FIXED_P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    FIXED_P8 = [6, 3, 7, 4, 8, 5, 10, 9]
    FIXED_P4 = [2, 4, 3, 1]

    S0 = [[1, 0, 3, 2],
          [3, 2, 1, 0],
          [0, 2, 1, 3],
          [3, 1, 3, 2]]

    S1 = [[0, 1, 2, 3],
          [2, 0, 1, 3],
          [3, 0, 1, 0],
          [2, 1, 0, 3]]

    KEY = '0111111101'

    with open('oliverorig') as myfile:
        plaintext_full = myfile.read().replace('\n', '')

    plaintext = plaintext_full[10000:11000]

    plaintext_binary = text_to_bits(plaintext)
    
    ciphertext_binary = []
    for i in range(0,len(plaintext_binary),8):
        ciphertext_binary.append(encrypt_sdes(plaintext_binary[i:i+8]))
    #print ciphertext_binary
        
    alphbet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '
    binary_dic = dict()
    count = 0
    for item in ciphertext_binary:
        if not item in binary_dic.keys():
            binary_dic[item] = alphbet[count]
            count += 1
            print count
    print binary_dic

    cipher_list = []
    for item in ciphertext_binary:
        cipher_list.append(binary_dic[item])
    ciphertext = ''.join(cipher_list)
    
    output = decrypt_substitution(ciphertext,bigram_reference)
    text_out = encrypt_substitution(ciphertext,output[0])
    print output
    print text_out
    print text_out == plaintext
    print logpi(plaintext,bigram_reference)

    
    
##    target = oliverorig_string[42000:43000]
##    bits = text_to_bits(target)
##    L_encrypted_bits = []
##    for i in range(0,len(bits),8):
##        L_encrypted_bits.append(encrypt(bits[i:i+8]))
##    encrypted_bits = ''.join(L_encrypted_bits)
##    #print target
##    #SDES_encrypted_text = encrypt(target,SUB_key)
##    #encrypted_text = encrypt_transposition(encrypt_substitution(target,SUB_key),len(target),TRAN_key,10)
##    #print encrypted_text



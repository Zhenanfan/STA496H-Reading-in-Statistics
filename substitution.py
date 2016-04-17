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
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
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
    i,j = np.random.randint(26,size = 2)
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
    x = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
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




if __name__ == '__main__':
    bigram_reference = dict()
    unigram_reference = dict()

    with open('warorig') as f:
        for line in f:
           bigram_reference = update_bigram(line,bigram_reference)
           unigram_reference = update_unigram(line,unigram_reference)

           
    with open('oliverorig') as myfile:
        plaintext_full = myfile.read().replace('\n', '')
    
    plaintext = plaintext_full[10000:12000]
    key_s = 'XEBPROHYAUFTIDSJLKZMWVNGQC'
    ciphertext1 = encrypt_substitution(plaintext,key_s)
    ciphertext = decrypt_unigram(ciphertext1 ,unigram_reference)
    output = decrypt_substitution(ciphertext,bigram_reference)
    text_out = encrypt_substitution(ciphertext,output[0])
    print output
    print text_out
    print text_out == plaintext
    print logpi(plaintext,bigram_reference)

    






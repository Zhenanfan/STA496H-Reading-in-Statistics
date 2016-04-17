from string import maketrans
import random
import numpy as np
import time
import operator


def update_bigram(text,bigram):
    for i in range(0, len(text)):
        temp = text[i:i+2]
        bigram[temp] = bigram.get(temp,0) + 1
    return bigram

# len(text) = len(key)
def encrypt_transposition(text,textlength,key,keylength):
    ciphertext = []
    l = textlength/keylength
    for i in range(l):
        for char in key:
            if char in '0123456789':
                index = int(char)
            else:
                index = ord(char) - 87
            ciphertext.append(text[i*keylength+index])
    return ''.join(ciphertext)


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
    	l = l + bigram_train[beta]*np.log(bigram_reference.get(beta,0)+0.1)
    return l

def slidemove(testkey,keylength):
    n = random.randint(0,keylength - 2)
    k1 = random.randint(0,keylength - n + 1)
    k2 = random.randint(0,keylength - n + 1)
    p1 = min(k1,k2)
    p2 = max(k1,k2)
    key1 = testkey[0:p1]
    key2 = testkey[p1:p1+n]
    key3 = testkey[p1+n:p2+n]
    key4 = testkey[p2+n:keylength]
    testkey_new = ''.join([key1,key3,key2,key4])
    return testkey_new


def decrypt_transposition(ciphertext,bigram_reference,keylength,M):
    textlength = len(ciphertext)
##    x = '0123456789'
##    x = '01234'
##    x = '0123456789abcde'
    x = '0123456789abcdefghij'
    xlist = []
    xlist.append(x)
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    p = 1
    for i in range(M):
        y = slidemove(x,keylength)
        u = np.random.uniform(0,1)
        ciphertext2 = encrypt_transposition(ciphertext,textlength,y,keylength)
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

def decrypt_transposition2(ciphertext,bigram_reference,keylength,M):
    textlength = len(ciphertext)
##    x = '0123456789'
##    x = '01234'
##    x = '0123456789abcde'
    x = '0123456789abcdefghij'
    xlist = []
    xlist.append(x)
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    for i in range(M):
        tau = (M/(500.0*(i+1)))**2
        p = 1.0/tau
        y = slidemove(x,keylength)
        u = np.random.uniform(0,1)
        ciphertext2 = encrypt_transposition(ciphertext,textlength,y,keylength)
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
    with open('warorig') as f:
        for line in f:
           bigram_reference = update_bigram(line,bigram_reference)

    with open('oliverorig') as myfile:
        plaintext_full = myfile.read().replace('\n', '')
    
    plaintext = plaintext_full[0:500]
##    key_t = '1937045862'
##    key_t = '30412'
##    key_t = 'b20a561478c93de'
    key_t = '973f6g0i45d1eh2jbac8'
    textlength = len(plaintext)
    keylength = len(key_t)
    ciphertext = encrypt_transposition(plaintext,textlength,key_t,keylength)
    nsuccess = 0
    Accuracy = 0
    for q in range(20):
        start_time = time.time()
        output = decrypt_transposition2(ciphertext,bigram_reference,keylength,5000)
        text_out = encrypt_transposition(ciphertext,textlength,output[0],keylength)
        accuracy = map(operator.eq, text_out, plaintext).count(True)/1000.0
        print '---Done in {} seconds---'.format(time.time() - start_time)
        print 'MAx score is {}'.format(output[2])
        print 'Theoritical max score is {}'.format(logpi(plaintext,bigram_reference))
        print 'Accuracy = {}'.format(accuracy)
        print text_out == plaintext
        if text_out == plaintext:
            nsuccess = nsuccess + 1
        Accuracy = Accuracy + accuracy
    print 'There are {} successful runs out of 20'.format(nsuccess)
    print 'Average accuracy = {}'.format(Accuracy/20.0)

    






from string import maketrans
import random
import numpy as np
import operator
import time


def update_bigram(text,bigram):
    for i in range(0, len(text)):
        temp = text[i:i+2]
        bigram[temp] = bigram.get(temp,0) + 1
    return bigram

def logpi(ciphertext,bigram_reference):
    bigram_reference.pop("\n", None)
    bigram_reference.pop(" \n", None)
    bigram_train = dict()
    for i in range(len(ciphertext)):
        temp = ciphertext[i:i+2]
        bigram_train[temp] = bigram_train.get(temp,0) + 1
    l = 0
    for beta in bigram_train.keys():
    	l = l + bigram_train[beta]*np.log(bigram_reference.get(beta,0)+1)
    return l


def swap2(testkey_substitution2):
    testkey_new = np.copy(testkey_substitution2)
##    i,j = np.random.randint(27,size = 2)
##    d = random.randint(0,1)
##    if d == 0:
##        l = testkey_new[i,:]
##        testkey_new[i,:] = testkey_new[j,:]
##        testkey_new[j,:] = l
##    else:
##        l = testkey_new[:,i]
##        testkey_new[:,i] = testkey_new[:,j]
##        testkey_new[:,j] = l
    i,j,l,k = np.random.randint(26,size = 4)
    testkey_new[i,j],testkey_new[l,k] = testkey_new[l,k],testkey_new[i,j]
    return testkey_new

def swap4(testkey_substitution2):
    testkey_new = testkey_substitution2
    i1,i2,i3,i4,i5,i6,i7,i8 = np.random.randint(26,size = 8)
    a = testkey_new[i1,i2]
    testkey_new[i1,i2] = testkey_new[i3,i4]
    testkey_new[i3,i4] = testkey_new[i5,i6]
    testkey_new[i5,i6] = testkey_new[i7,i8]
    testkey_new[i7,i8] = a
    return testkey_new

def swap8(testkey_substitution2):
    testkey_new = testkey_substitution2
    i1,i2,i3,i4,i5,i6,i7,i8 = np.random.randint(26,size = 8)
    j1,j2,j3,j4,j5,j6,j7,j8 = np.random.randint(26,size = 8)
    a = testkey_new[i1,i2]
    testkey_new[i1,i2] = testkey_new[i3,i4]
    testkey_new[i3,i4] = testkey_new[i5,i6]
    testkey_new[i5,i6] = testkey_new[i7,i8]
    testkey_new[i7,i8] = testkey_new[j1,j2]
    testkey_new[j1,j2] = testkey_new[j3,j4]
    testkey_new[j3,j4] = testkey_new[j5,j6]
    testkey_new[j5,j6] = testkey_new[j7,j8]
    testkey_new[j7,j8] = a
    return testkey_new


def encrypt_block_2(encrypt_matrix, plaintext):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
##    order_matrix = np.arange(27**2).reshape(27,27)
##    encrypt_vector = encrypt_matrix.flatten()
    cipher_list = []
    i = 0
    while i < len(plaintext)-3:
        temp1 = plaintext[i:i+2]
        if temp1[0] == ' ':
            i = i+1
            cipher_list.append(' ')
        elif temp1[1] == ' ':
            temp1 = plaintext[i]+plaintext[i+2]
            i = i+3
            a = alphabet.index(temp1[0])
            b = alphabet.index(temp1[-1])
            code = encrypt_matrix[a,b]
            temp2 = divmod(code,26)
            cipher_list.append(alphabet[temp2[0]] + ' ' + alphabet[temp2[-1]])
        else:
            a = alphabet.index(temp1[0])
            b = alphabet.index(temp1[-1])
            code = encrypt_matrix[a,b]
            temp2 = divmod(code,26)
            cipher_list.append(alphabet[temp2[0]] + alphabet[temp2[-1]])
            i = i+2
    return ''.join(cipher_list)

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
    M = 2000000
    textlength = len(ciphertext)
    x = np.arange(26**2).reshape(26,26)
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    xlist = []
    for i in range(M):
        if i % 10000 == 0:
            print 'Iteration {}'.format(i)
        tau = 3000.0/(i+1)
        p = 1.0/tau
##        if i < M/10:
##            y = swap4(x)
####        elif i < 2*M/3:
####            y = swap4(x)
##        else:
##            y = swap2(x)
        y = swap2(x)
        ciphertext2 = encrypt_block_2(y, ciphertext)
        while '  ' in ciphertext2:
            y = swap2(x)
            ciphertext2 = encrypt_block_2(y, ciphertext)
        u = np.random.uniform(0,1)
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


def build_init_matrix(order_dict):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    init_matrix = np.random.choice(np.arange(26**2), replace=False, size=(26, 26))
    for key, value in order_dict.iteritems():
        a,b = alphabet.index(key[0]),alphabet.index(key[-1])
        c,d = alphabet.index(value[0]),alphabet.index(value[-1])
        index = 26*c + d 
        init_matrix[a,b] = index
    return init_matrix




if __name__ == '__main__':
    start_time = time.time()
    f = open('oliverorig', 'r')
    oliverorig_string = f.read().replace('\n', '')
    f.close()
    plaintext = oliverorig_string[10000:15000]
    uarray = np.random.choice(np.arange(26**2), replace=False, size=(26, 26))
    cipher = encrypt_block_2(uarray,plaintext)
    
    bigram_ref = dict()
    bigram_ref2 = dict()
    bigram_cipher = dict()
    bigram_cipher2 = dict()
    f = open('warorig', 'r')
    warorig = f.read().replace('\n', '')
    f.close()
    cipher2 = cipher.replace(' ','')
    warorig2 = warorig.replace(' ','')
    bigram_ref = update_bigram(warorig,bigram_ref)
    bigram_cipher = update_bigram(cipher,bigram_cipher)
    bigram_ref2 = update_bigram(warorig2,bigram_ref2)
    bigram_cipher2 = update_bigram(cipher2,bigram_cipher2)
    sorted_cipher = sorted(bigram_cipher2, key=lambda k: -bigram_cipher2[k])
    sorted_ref = sorted(bigram_ref2, key=lambda k: -bigram_ref2[k])
    order_dict = dict()
    i = 0
    max_index = len(sorted_ref)
    for item in sorted_cipher:
        if i < max_index:
            order_dict[item] = sorted_ref[i]
        else:
            order_dict[item] = item
        i += 1
    init_text = encrypt_block_2(build_init_matrix(order_dict),cipher)
    print logpi(cipher,bigram_ref)
    print logpi(init_text,bigram_ref)
    
    output = decrypt_substitution(init_text,bigram_ref)
    text_out = encrypt_block_2(output[0], init_text)
    accuracy = map(operator.eq, text_out, plaintext).count(True)/5000.0
    print '---Done in {} seconds---'.format(time.time() - start_time)
    print 'Max score is {}'.format(output[2])
    print 'Max score index is {}'.format(output[3])
    print 'Theoritical max score is {}'.format(logpi(plaintext,bigram_ref))
    print 'Acceptance rate is {}'.format(output[1]/2000000.0)
    print 'Accuracy is {}'.format(accuracy)
##    print text_out
    print text_out == plaintext
    


    







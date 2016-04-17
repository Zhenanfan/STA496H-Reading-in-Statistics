from string import maketrans
import random
import numpy as np
import operator
import time


 #You should tokenize your text
text = "I do not like green eggs and ham I do not like bla blabla them Sam I am"

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

def update_trigram(text,trigram):
    for i in range(0, len(text)-2):
        temp = text[i:i+3]
        #if ' ' in temp:
        #    continue
        trigram[temp] = trigram.get(temp,0) + 1
    return trigram

def update_eighthgram(text,eighthgram):
    for i in range(len(text)-7):
        temp = text[i:i+8]
        eighthgram[temp] = eighthgram.get(temp,0) + 1
    return eighthgram


# len(text) = len(key)
def encrypt_transposition(text,textlength,key,keylength):
    ciphertext = []
    l = textlength/keylength
    for i in range(l):
        for char in key:
            index = int(char)
            ciphertext.append(text[i*keylength+index])
    return ''.join(ciphertext)


def encrypt_substitution(text, key):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    translation = maketrans(alphabet, key)
    return text.translate(translation)
    


def logpi(ciphertext,bigram_reference):
##    text1 = encrypt_substitution(text, key_s)
##    textlength = len(plaintext)
##    keylength = len(key_t)
##    ciphertext = encrypt_transposition(plaintext,textlength,key_t,keylength)
    bigram_train = dict()
    for i in range(len(ciphertext)-1):
        temp = ciphertext[i:i+2]
        bigram_train[temp] = bigram_train.get(temp,0) + 1
    l = 0
    for beta in bigram_train.keys():
    	l = l + (bigram_train[beta]+1)*np.log(bigram_reference.get(beta,0)+1)
    return l

def logpi_tri(text,trigram_reference):
    trigram_train = {}
    for i in range(0, len(text)-2):
        temp = text[i:i+3]
        #if ' ' in temp:
        #    continue
        trigram_train[temp] = trigram_train.get(temp,0) + 1
    l = 0
    #for beta in bigram_reference.keys():
    #    l = l + bigram_train.get(beta,0)*np.log(bigram_reference[beta])
    #return l
    for beta in trigram_train.keys():
        l = l + (trigram_train[beta]+1)*np.log(trigram_reference.get(beta,0)+1)
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


def decrypt_substitution(ciphertext,bigram_reference,key_initial):
    M = 3000
    textlength = len(ciphertext)
    x = key_initial
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

def decrypt_transposition(ciphertext,bigram_reference,key_initial,keylength):
    M = 1000
    textlength = len(ciphertext)
    x = key_initial
    xlist = []
    xlist.append(x)
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    for i in range(M):
        tau = 1.0/(i+1)
        p = 1.0/tau
        y = slidemove(x,10)
        u = np.random.uniform(0,1)
        ciphertext2 = encrypt_transposition(ciphertext,textlength,y,10)
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
    



def decrypt(ciphertext,bigram_reference,key_tlength):
##    start_time = time.time()
    M = 30000
    textlength = len(ciphertext)
    x = ['0123456789','ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    x0list = []
    x0list.append(x[0])
    x1list = []
    x1list.append(x[1])
    scorelist = []
    scorelist.append(logpi(ciphertext,bigram_reference))
    naccept = 0
    for i in range(M):
        if i % 5000 == 0:
            print 'Iteration {}'.format(i)
        tau = 30.0/(i+1)
        p = 1.0/tau
##        if i%2 == 0:
##            y0 = slidemove(x[0],10)
##            y1 = x[1]
##        if i%2 == 1:
##            y0 = x[0]
##            y1 = swap(x[1])
        y0 = slidemove(x[0],10)
        y1 = swap(x[1])
        u = np.random.uniform(0,1)
        ciphertext2 = encrypt_transposition(ciphertext,textlength,y0,10)
        ciphertextb = encrypt_substitution(ciphertext2, y1)
        score_new = logpi(ciphertextb,bigram_reference)
        alpha = p*(score_new - scorelist[i])
        if np.log(u) < alpha :
            x = [y0,y1]
            naccept = naccept + 1
            scorelist.append(score_new)
        else:
            scorelist.append(scorelist[i])
        x0list.append(x[0])
        x1list.append(x[1])
    index = scorelist.index(max(scorelist))
##    print '---Done in {} seconds---'.format(time.time() - start_time)
    return [x0list[index],x1list[index],naccept,max(scorelist),index]




if __name__ == '__main__':
    bigram_reference = dict()
    unigram_reference = dict()

    with open('oliverorig') as f:
        for line in f:
           bigram_reference = update_bigram(line,bigram_reference)
           unigram_reference = update_unigram(line,unigram_reference)


         
    with open('warorig') as myfile:
        plaintext_full = myfile.read().replace('\n', '')
##    with open('icehock') as myfile:
##        plaintext_full = myfile.read().replace('\n', '')
    
    
    plaintext = plaintext_full[10000:12000]
    key_t = '1937045862'
    key_s = 'XEBPROHYAUFTIDSJLKZMWVNGQC'
    textlength = len(plaintext)
    keylength = len(key_t)
    ciphertext1 = encrypt_transposition(plaintext,textlength,key_t,keylength)
    ciphertext2 = encrypt_substitution(ciphertext1,key_s)
    ciphertext = decrypt_unigram(ciphertext2 ,unigram_reference)
    Accuracy = 0
    nsuccess = 0
    for q in range(20):
        print '---{}th Run'.format(q+1)
        start_time = time.time()
        output = decrypt(ciphertext,bigram_reference,10)
##        text_out1 = encrypt_transposition(ciphertext,textlength,output[0],10)
##        text_out = encrypt_substitution(text_out1,output[1])
        print 'Cycle 1'
        cycletext0 = encrypt_transposition(ciphertext,textlength,output[0],10)
        output1 = decrypt_substitution(cycletext0,bigram_reference,output[1])
        cycletext1 = encrypt_substitution(ciphertext, output1[0])
        output2 = decrypt_transposition(cycletext1,bigram_reference,output[0],keylength)
        print 'Cycle 2'
        cycletext2 = encrypt_transposition(ciphertext,textlength,output2[0],10)
        output3 = decrypt_substitution(cycletext2,bigram_reference,output1[0])
        cycletext3 = encrypt_substitution(ciphertext, output3[0])
        output4 = decrypt_transposition(cycletext3,bigram_reference,output2[0],keylength)
        print 'Cycle 3'
        cycletext4 = encrypt_transposition(ciphertext,textlength,output4[0],10)
        output5 = decrypt_substitution(cycletext4,bigram_reference,output3[0])
        cycletext5 = encrypt_substitution(ciphertext, output5[0])
        output6 = decrypt_transposition(cycletext5,bigram_reference,output4[0],keylength)
        text_out = encrypt_transposition(cycletext5,textlength,output6[0],10)
        accuracy = map(operator.eq, text_out, plaintext).count(True)/2000.0
        print '---Done in {} seconds---'.format(time.time() - start_time)
        print 'MAx score is {}'.format(output6[2]) 
        print 'Theoritical max score is {}'.format(logpi(plaintext,bigram_reference))
        print text_out == plaintext
        if text_out == plaintext:
            nsuccess = nsuccess + 1
        Accuracy = Accuracy + accuracy
    print 'There are {} successful runs out of 20'.format(nsuccess)
    print 'Average accuracy = {}'.format(Accuracy/20.0) 
        
##    output = decrypt(ciphertext,bigram_reference,10)
##    text_out1 = encrypt_transposition(ciphertext,textlength,output[0],10)
##    text_out = encrypt_substitution(text_out1,output[1])
##    print 'Decryption transiposition key is ' + output[0]
##    print 'Decryption substitution key is ' + output[1]
##    print 'MAx score is {}'.format(output[3]) + 'and it appears at iteration {}'.format(output[4])
##    print 'Theoritical max score is {}'.format(logpi(plaintext,bigram_reference))
##    print text_out


##    text_out1 = encrypt_transposition(ciphertext,textlength,output[0],keylength)
##    text_out = encrypt_substitution(text_out1,output[1])
##    output1 = decrypt_transposition(text_out,bigram_reference,output[0],keylength)
##    text_outt = encrypt_transposition(text_out,textlength,output1[0],keylength)
##    output2 = decrypt_substitution(text_outt,bigram_reference,output[1])
##    print 'Decryption transiposition key is ' + output1[0]
##    print 'Decryption substitution key is ' + output2[0]
##    print 'MAx score is {}'.format(output2[2]) 
##    print 'Theoritical max score is {}'.format(logpi(plaintext,bigram_reference))
##    print encrypt_substitution(text_outt,output2[0])

    






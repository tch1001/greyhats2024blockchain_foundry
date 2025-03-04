

# This file was *autogenerated* from the file sol.sage
from sage.all_cmdline import *   # import sage library

_sage_const_2 = Integer(2); _sage_const_9999 = Integer(9999); _sage_const_100 = Integer(100); _sage_const_0p05 = RealNumber('0.05'); _sage_const_6 = Integer(6); _sage_const_1 = Integer(1); _sage_const_0 = Integer(0); _sage_const_10000 = Integer(10000); _sage_const_200 = Integer(200); _sage_const_20 = Integer(20)
from pwn import *
import numpy as np
from ldpc import bp_decoder, code_util


def matrix_to_bits(G):
    return "".join([str(x) for x in G.flatten()])

def bits_to_matrix(s):
    return np.array([[int(s[i * k + j]) for j in range(k)] for i in range(n)]) % _sage_const_2 

def bits_to_vector(s):
    return np.array([int(x) for x in s])

r = remote("localhost", int(_sage_const_9999 ))

n = _sage_const_100 
k = int(n * _sage_const_2 )
threshold = _sage_const_0p05 
tt = _sage_const_6 
arr = [_sage_const_1 ] * tt + [_sage_const_0 ] * (k - tt)

H = []

for i in range(k - n):
    temp = []
    random.shuffle(arr)
    H.append(arr.copy())

H = np.array(H)
G = code_util.construct_generator_matrix(H)

r.recvuntil("Option:")
r.sendline("1")
r.sendline(matrix_to_bits(G))

r.recvuntil("M:")
M = bits_to_matrix(r.recvline().strip().decode())

C = LinearCode(Matrix(GF(_sage_const_2 ), M))
H = C.parity_check_matrix().change_ring(ZZ).LLL().change_ring(GF(_sage_const_2 )).numpy(dtype=int)

bpd=bp_decoder(
    H, #the parity check matrix
    error_rate=threshold, # the error rate on each bit
    max_iter=_sage_const_10000 , #the maximum iteration depth for BP
    bp_method="product_sum", #BP method. The other option is `minimum_sum'
    channel_probs=[None] #channel probability probabilities. Will overide error rate.
)

# Weight 1

dic = {}

error = np.zeros(k,dtype=int)
key = tuple(list(H @ error.transpose() % _sage_const_2 ))
dic[key] = [error]

for i in range(k):
    error = np.zeros(k,dtype=int)
    error[i] = _sage_const_1 
    key = tuple(list(H @ error.transpose() % _sage_const_2 ))
    if (key not in dic):
        dic[key] = []
    dic[key].append(error)

# Weight 2

for i in range(k):
    for j in range(i + _sage_const_1 , k):
        error = np.zeros(k,dtype=int)
        error[i] = _sage_const_1 
        error[j] = _sage_const_1 
        key = tuple(list(H @ error.transpose() % _sage_const_2 ))
        if (key not in dic):
            dic[key] = []
        dic[key].append(error)

r.sendline("3")
for i in range(_sage_const_200 ):
    r.recvuntil("c:")
    encoded = bits_to_vector(r.recvline().strip().decode())
    decoded_codeword = bpd.decode(encoded)

    key = tuple(list(H @ decoded_codeword.transpose() % _sage_const_2 ))

    if (key in dic):
        ttt = _sage_const_0 
        for i in range(len(dic[key])):
            if (ttt >= _sage_const_20 ):
                break
            temp = (decoded_codeword + dic[key][i]) % _sage_const_2 
            try:
                guess = Matrix(GF(_sage_const_2 ), M).solve_left(vector(GF(_sage_const_2 ), temp))
                ttt += _sage_const_1 
                r.sendline(matrix_to_bits(guess.numpy(dtype=int)))
            except KeyboardInterrupt:
                exit()
            except e:
                print(e)
                pass
        for _ in range(_sage_const_20  - ttt):
            r.sendline(matrix_to_bits(decoded_codeword))
    else:
        for _ in range(_sage_const_20 ):
            r.sendline(matrix_to_bits(decoded_codeword))
    

r.interactive()



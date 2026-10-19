import sys, math

def cdf(k, n, p):  # P(X <= k)
    return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k+1))

def bisect(f, lo=0.0, hi=1.0, it=100):
    for _ in range(it):
        m = (lo + hi) / 2
        if f(m): hi = m
        else: lo = m
    return (lo + hi) / 2

def cp_lower(k, n, a):
    return 0.0 if k == 0 else bisect(lambda p: 1 - cdf(k-1, n, p) >= a)

def cp_upper(k, n, a):
    return 1.0 if k == n else bisect(lambda p: cdf(k, n, p) <= a)

k, n = int(sys.argv[1]), int(sys.argv[2])
z = 1.959964
p = k / n
den = 1 + z**2 / n
c = (p + z**2 / (2*n)) / den
h = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / den
lo1 = cp_lower(k, n, 0.05)

print(f"Precisao pontual      : {p:.4f} ({k}/{n})")
print(f"Wilson 95%            : [{max(0,c-h):.4f}, {min(1,c+h):.4f}]")
print(f"Clopper-Pearson 95%   : [{cp_lower(k,n,0.025):.4f}, {cp_upper(k,n,0.025):.4f}]")
print(f"Lim. inf. 1-lado 95%  : {lo1:.4f} -> regua 0.95: {'OK' if lo1 >= 0.95 else 'NAO GARANTIDA'}")
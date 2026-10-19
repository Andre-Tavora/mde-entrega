from math import comb
N, n, x = 87, 62, 1
def p_le(K): return sum(comb(K,i)*comb(N-K,n-i) for i in range(0, min(x,K)+1)) / comb(N,n)
Kmax = max(K for K in range(x, N-n+x+1) if p_le(K) >= 0.05)
print(f"Amostra: {n-x}/{n} certas | N publicar = {N}")
print(f"Erros max na populacao (95% 1-lado): {Kmax}")
print(f"Precisao minima garantida: {(N-Kmax)/N:.4f} -> regua 0.95: {'GARANTIDA' if (N-Kmax)/N>=0.95 else 'NAO GARANTIDA'}")
for K in range(x, Kmax+3): print(f"  K={K}: P(X<={x}) = {p_le(K):.4f}")

from math import fabs, sqrt

min_delta = 5e-15
max_steps = 30000

def bairstow(a, n):
    if n == 2:
        b2 = a[n]
        b1 = a[n-1]
        b0 = a[n-2]
        d = b1*b1 - 4*b2*b0
        if d > 0: return True, [(-b1 - sqrt(d)) / (2*b2), (-b1 + sqrt(d)) / (2*b2)]
        elif d == 0: return True, [-b1 / (2*b2)]
        else: return True, []
    elif n == 1:
        b1 = a[n]
        b0 = a[n-1]
        return True, [-b0/b1]
    elif n < 1:
        return False, []

    u, v = a[n-1]/a[n], a[n-2]/a[n]

    b = dict()
    b[n] = 0
    b[n-1] = 0
    f = dict()
    f[n] = 0
    f[n-1] = 0

    delta = 1
    steps = 0
    while delta > min_delta and steps < max_steps:
        steps += 1
        b0, b1, b2 = 0, 0, 0
        f0, f1, f2 = 0, 0, 0

        for i in range(n-2, -1, -1):
            b2, b1 = b1, b0
            f2, f1 = f1, f0
            b0 = a[i+2] - u * b1 - v * b2
            f0 = b2 - u * f1 - v * f2

        c = a[1] - u * b0 - v * b1
        d = a[0] - v * b0
        g = b1 - u * f0 - v * f1
        h = b0 - v * f0

        z = v*g*g + h*(h - u*g)
        ud = (g*d - h*c)/z
        vd = (d*(g*u - h) - g*v*c)/z
        delta = fabs(ud) + fabs(vd)
        u, v = u - ud, v - vd

    if steps == max_steps:
        print('steps!', delta)
        return False, []

    d = u*u - 4*v
    if d > 0: roots = [(-u - sqrt(d)) /2, (-u + sqrt(d)) / 2]
    elif d == 0: roots = [-u/2]
    else: roots = []
    b = dict()
    b[n-2] = a[n]
    b[n-3] = a[n-1] - u*b[n-2]
    for i in range(n - 4, -1, -1):
        b[i] = a[i + 2] - u * b[i+1] - v * b[i+2]
    er, res = bairstow(b, n - 2)
    if not er: return False, []
    return True, roots + res

def get_fx(a, n):
    def fx(x):
        q = a[n]
        for i in range(n, 0, -1):
            q = q*x + a[i-1]
        return q
    return fx

def accur_roots(a, n, roots):
    """	f = get_fx(a, n)
	new_roots = list()
	for r in roots:
		step = min_delta
		#print(step, f(r), f(r+step), f(r-step))
		if fabs(f(r + step)) < fabs(f(r)): step = step
		elif fabs(f(r - step)) < fabs(f(r)): step = -step
		else:
			new_roots.append(r)
			continue

		while f(r + step) < f(r):
			r = r + step
			step = step / 2

		new_roots.append(r)
	return new_roots"""
    return roots

def get_poly_roots(a, n):
    er, roots = bairstow(a, n)
    #if er == True: roots = accur_roots(a, n, roots)
    #else: print('error!')
    return er, roots

if __name__ == '__main__':
    a = dict({5: 6, 4: 11, 3: -33, 2: -33, 1: 11, 0: 6})
    f = get_fx(a, 5)
    er, roots = bairstow(a, 5)
    if not er: print('error on solve')
    else:
        if len(roots) > 0:
            for x in roots:
                print(x, f(x))
        else: print('no roots')

    print('*' * 30)
    er, roots = get_poly_roots(a, 5)
    if not er: print('error on solve')
    else:
        if len(roots) > 0:
            for x in roots:
                print(x, f(x))
        else: print('no roots')


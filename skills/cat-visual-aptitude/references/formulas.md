# Formula and shortcut sheet

Use these in the script, not in prose. Every formula here is a place a sign or an
exponent goes wrong when done mentally.

## Percentages and growth

```
pct_change(old, new)      = (new - old) / old * 100
pct_point(a_pct, b_pct)   = b_pct - a_pct                 # NOT a percentage change
reverse(after, pct)       = after / (1 + pct/100)         # original before a rise
successive(p1, p2, ...)   = (Π (1 + pi/100) - 1) * 100
cagr(start, end, n)       = ((end/start) ** (1/n) - 1) * 100    # n = INTERVALS
avg_growth(start, end, n) = (end - start) / n             # absolute, per interval
share(part, whole)        = part / whole * 100
index(value, base_value)  = value / base_value * 100
value_from_index(idx, base_value) = idx / 100 * base_value
```

Fraction ↔ percentage table worth recognising on sight (it turns division into
recall): 1/2 50 · 1/3 33.33 · 1/4 25 · 1/5 20 · 1/6 16.67 · 1/7 14.29 · 1/8 12.5 ·
1/9 11.11 · 1/11 9.09 · 1/12 8.33 · 1/13 7.69 · 1/14 7.14 · 1/15 6.67 · 1/16 6.25 ·
3/8 37.5 · 5/8 62.5 · 7/8 87.5 · 2/7 28.57 · 3/7 42.86.

Useful identities:
- A is x% more than B ⇒ B is `x/(100+x)*100` % less than A.
- A rise of x% followed by a fall of x% is a net `-x²/100` %.
- To keep a product constant, if one factor rises x%, the other must fall
  `x/(100+x)*100` %.

## Averages, ratios, mixtures

```
weighted_mean(values, weights) = Σ(v*w) / Σw
alligation: (mean - cheap) / (dear - mean) = qty_dear / qty_cheap
replacement: after n replacements of fraction f, pure left = initial * (1-f)**n
```

- Average of percentages is only valid when the bases are equal.
- If the average of n numbers is A and one number changes by d, the average
  changes by d/n.
- Ratio A : B : C combining A : B = a : b and B : C = c : d is `ac : bc : bd`.

## Interest

```
SI  = P * r * t / 100
CI  = P * ((1 + r/100) ** t - 1)
CI, k times a year: P * ((1 + r/(100k)) ** (k*t) - 1)
CI - SI for 2 years = P * (r/100) ** 2
half-yearly for t years: rate r/2, periods 2t
```

Instalments, depreciation and population growth are compound interest in disguise.

## Time, speed, distance and work

```
speed = distance / time;  average speed over equal distances = 2ab/(a+b)
relative speed: same direction |a-b|, opposite a+b
train past a pole: length/speed;  past a platform: (length+platform)/speed
boats: downstream b+s, upstream b-s
work: rate = 1/time; combined rate = Σ rates
n people, m days, h hours: work ∝ n*m*h
```

Use an LCM base for work problems (if A takes 12 and B takes 18 days, total work
= 36 units) so every rate is an integer.

## Numbers

```
divisors of p^a * q^b * ... = (a+1)(b+1)...
sum of divisors = Π (p^(a+1) - 1)/(p - 1)
number of trailing zeros in n! = Σ floor(n / 5^i)
highest power of prime p in n! = Σ floor(n / p^i)
a ≡ b (mod m) arithmetic; Fermat: a^(p-1) ≡ 1 (mod p) for prime p ∤ a
Euler: a^φ(n) ≡ 1 (mod n) when gcd(a,n)=1
units digit cycles with period 4 for most bases
gcd(a,b) * lcm(a,b) = a*b
```

For remainders, digit sums and cyclicity, **verify the pattern by brute force over
a range in the script** rather than trusting the recalled rule.

## Progressions, functions, logs

```
AP: a_n = a + (n-1)d;  S_n = n/2 * (2a + (n-1)d) = n * (first + last)/2
GP: a_n = a*r^(n-1);   S_n = a(r^n - 1)/(r - 1);  S_inf = a/(1-r) for |r|<1
HP: reciprocals form an AP
Σn = n(n+1)/2 · Σn² = n(n+1)(2n+1)/6 · Σn³ = (n(n+1)/2)²
AM ≥ GM ≥ HM, equality iff all equal
log(ab)=log a+log b · log(a/b)=log a−log b · log(a^n)=n log a · log_b a = log a / log b
```

## Counting and probability

```
nPr = n!/(n-r)!        nCr = n!/(r!(n-r)!)
arrangements of n with repeats: n! / Π(count_i!)
circular arrangements of n: (n-1)!;  necklace (reflections same): (n-1)!/2
at least one: 1 - P(none)
distributing n identical into r distinct, each ≥ 0: C(n+r-1, r-1)
                                       each ≥ 1: C(n-1, r-1)
derangements D(n) = n! * Σ (-1)^k / k!
inclusion-exclusion for |A∪B∪C| — see sets.py
```

Validate any counting formula by enumerating a small case (n = 4 or 5) in the
script before applying it to the real n.

## Mensuration

```
triangle: area = 1/2*b*h = sqrt(s(s-a)(s-b)(s-c)) = 1/2*a*b*sin C
          R = abc/(4*area);  r = area/s
equilateral side a: area = sqrt(3)/4*a²; height = sqrt(3)/2*a
circle: area πr², circumference 2πr; sector θ°: πr²θ/360, arc 2πrθ/360
trapezium: 1/2*(a+b)*h
sphere: 4πr² surface, 4/3πr³ volume
cone: πrl curved, πr(l+r) total, 1/3πr²h volume, l² = r² + h²
cylinder: 2πrh curved, 2πr(h+r) total, πr²h volume
cuboid: 2(lb+bh+hl), volume lbh, diagonal sqrt(l²+b²+h²)
similar figures: lengths k, areas k², volumes k³
```

Coordinate geometry:
```
distance sqrt((x2-x1)²+(y2-y1)²);  section formula ((mx2+nx1)/(m+n), ...)
area of triangle = 1/2 |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
line through 2 points; perpendicular slopes multiply to -1
distance from point to line ax+by+c=0: |ax0+by0+c|/sqrt(a²+b²)
```

Placing a figure on coordinates and computing in the script is almost always
faster and safer than a synthetic argument.

## Quick estimation discipline

Only when the stem says "approximately" and the options are more than ~5% apart:

- Round to 2 significant figures, keep a running note of whether you rounded up or
  down, and check the answer still separates the options.
- Then confirm with the exact computation anyway if it costs one extra line in the
  script — it usually does.

n = 7
l = 0
for i in range(1, n):
    print(i)
    l += 1
    if l == 5 or i == n - 1:
        print(f'load: {i}')
        l = 0
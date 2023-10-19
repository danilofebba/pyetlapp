n = 7
l = 0
for i in range(1, n):
    print(i)
    l += 1
    if l == 5 or i == n - 1:
        print(f'load: {i}')
        l = 0

####################################################################################################################

import concurrent.futures
import time

def write_file(n_files, n_row):
    ti = time.time()
    file = open(f'file{n_files}.csv', 'w')
    file.write('code;description\n')
    for i in range(1, n_row):
        file.write(f'{i};description{i}\n')
    file.close()
    return f'name: file{n_files}.csv - time:{round(time.time() - ti, 3)}'

%%time
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(write_file, f, 10000000) for f in range(1, 10)]
    for future in concurrent.futures.as_completed(futures):
        try:
            print(future.result())
        except Exception as e:
            print(e)

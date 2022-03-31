import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filename = sys.argv[1]
my_data = pd.read_csv(filename, sep='\t',  header=None).dropna(how='any')

# 「446,415:58:49」のような，よくわからないのがある．
line = 0
for i in range(len(my_data)):
    if len(my_data.iloc[i, 4]) > 8:
        line = i
        break

if line != 0: my_data = my_data.iloc[:line, ]

def g(s):
    try:
        return s[0] == '-'
    except:
        print(f'{filename}:{s}')

#時間の負号だけ別にする
my_data[7] = [-1 if g(s) else 1 for s in my_data[4]]
my_data[4] = [s.replace('-', '') for s in my_data[4]]
my_data[4] = [f'0:{s}' if len(s) <= 5 else s for s in my_data[4]]

#経過時間を秒で表す
tmp = pd.to_datetime(my_data[4], format='%H:%M:%S') - pd.to_datetime('1900-01-01 00:00:00')
my_data[8] = [d.seconds for d in tmp]
my_data[8] = my_data[8] * my_data[7]

#日本円だけ扱う
def f(s):
    if isinstance(s, int) or isinstance(s, float): return s
    if s[0] == '¥':
        return int(s[1:].replace(',', ''))
    return 0

#金額を数値にし，累積値を計算する
my_data[9] = [f(s) for s in my_data[5]] #金額
my_data[10] = np.cumsum(my_data[9]) #累積

#経過時間と累積金額をグラフにする
df = pd.DataFrame({'t':my_data[8], 'amount':my_data[10]})
df.plot(x='t')

f = filename.replace('.tsv', '')
plt.savefig(f'{f}.pdf')
plt.savefig(f'{f}.png')
plt.clf()

superchats = my_data[my_data[9] != 0]
with open(f'{f}-stat.txt', 'w') as file:
    n = len(superchats)
    if n == 0:
        file.write(f'{f},0,0,0,0,0,0,0')
    else:
        tmp = superchats[9]
        file.write(f'{f},{n},{sum(tmp)},{np.mean(tmp)},{np.std(tmp)},{np.min(tmp)},{np.median(tmp)},{np.max(tmp)}')
    file.write('\n')

plt.xlabel('amount')
plt.ylabel('n')
plt.hist(superchats[9])

plt.savefig(f'{f}-hist.pdf')
plt.savefig(f'{f}-hist.png')

df.to_csv(f'{f}.csv', index=False)

tmp = pd.DataFrame({'name':my_data[3],'money':my_data[9]})
tmp = tmp[tmp['money'] != 0]
tmp.to_csv(f'{f}-money.csv', index=False, header=False)

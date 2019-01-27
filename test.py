n = [{'a':1},{'a':2},{'a':3},{'a':2},{'a':5},{'a':3},{'a':1}]
tmp = []
chk_flg = []

for i in n:
    if i['a'] not in chk_flg:
        tmp.append(i)
        chk_flg.append(i['a'])
        
print(tmp)

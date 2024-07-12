import re

key = "_"
abc = '0abcdefghi'

dic1 = {
"대회명" : "Event",
"회전" : "Round",
"대국일자" : "Date",
"대국장소" : "Site",
"초대국자" : "White",
"한대국자" : "Black",
"제한시간" : "TimeControl",
'대국결과' : "Result",
"한 완승" : "0-1",
"초 완승" : "1-0",
"한 시간승" : "0-1",
"초 시간승" : "1-0",
"한 기권승" : "0-1",
"초 기권승" : "1-0"
}
dic2 = {
'초차림 "마상마상"' : [1,"RHEA1AHER"],
'한차림 "마상마상"' : [0,"rhea1aher"],
'초차림 "마상상마"' : [1,"RHEA1AEHR"],
'한차림 "마상상마"' : [0,"rhea1aehr"],
'초차림 "상마마상"' : [1,"REHA1AHER"],
'한차림 "상마마상"' : [0,"reha1aher"],
'초차림 "상마상마"' : [1,"REHA1AEHR"],
'한차림 "상마상마"' : [0,"reha1aehr"]
}

fen = [0,0]

def tryint(maxn = 100,s=""):
    try : 
        a = int(input(s))
        if (0<=a<=maxn):
            return a
        elif a== -1:
            return a
        else:
            print("메뉴에 있는 번호를 선택해 주세요.")
            a = tryint()
            return a
    except: 
        print("숫자를 입력해 주세요.")
        a = tryint()
        return a

def trygib():
    try:
        name = input(f"기보명 입력(ex. shar{key}cellt or cellt) : ")
        if name.count(key)==0:
            path = f"{name}.gib"
            f = open(path, 'r')
        else:
            path = f"../_프로/{name.split(key)[0]}/{name.split(key)[1]}/{name.split(key)[1]}.gib"
            f = open(path, 'r')
        return f.read(), path
    except KeyboardInterrupt:
        print("keyboard inturrupt")
    except:
        print("해당 위치에 기보가 없습니다.")
        return trygib()

    
def pgn(a, num):
    pgn = ""
    c = re.sub('[^0-9 .]',' ',a)
    for i in range(num,0,-1):
        c = c.replace(f'{i}. ', ' ')
    c = re.sub(' +', ' ', c).strip().split(' ')
    for i in range(num*2):
        if i%4 == 0:
            n = str(i//4+1)
            pgn+='\n'+n+'.'
        if i%2 == 0:
            pgn+=' '
        d = c[i]
        pgn += abc[int(d[1])]+str((10-int(d[0]))%10)
    return pgn


def save_file(content, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"입력된 내용이 '{file_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")


def main(a):
    #pattern = r'\[(.*?)\]'
    tag = re.findall(r'\[(.*?)\]', a)#리스트 형태임.
    tag = '['+']\n['.join(tag)+']'#복원형
    
    for key in dic2.keys():
        if key in a:
            fen[dic2[key][0]] = dic2[key][1]
    for key in dic1.keys():
        if key in a:
            tag = tag.replace(key, dic1[key])
    realfen = f'{tag}\n[Variant "janggicasual"]\n[VariantFamily "janggi"]\n[FEN "{fen[0]}/4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4/{fen[1]} w 0 1"]\n'
    return realfen


def main2(a,path,fen,s=''):
    save_file(fen+pgn(a,a.count('.')), path[:-4]+s+".pgn")


a, path = trygib()
c = a.split("\n\n")
v = []
if len(c) == 1:
    main2(c[0],path,main(c[0]))
else :
    chk = tryint(2,"1 : 합본(winboard 전용)\n2 : 개별 pgn")
    for i in range(0,len(c)-1,2):
        if chk == 1 or chk == 0:
            v.append(main(c[i]) + pgn(c[i+1],c[i+1].count('.')))
        if chk == 2 or chk == 0:
            main2(c[i+1],path,main(c[i]),str(i//2)) # 굴비, 윈보드 용 개별본
    if chk==1 or chk == 0:
        v = "\n*\n".join(v)
        save_file(v, path[:-3]+"pgn")#윈보드 용 합본
    

input()




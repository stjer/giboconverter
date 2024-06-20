import re

s = 'abcdefghi'

def en2ko(gib):
    en = 'ACEHKPR'
    ko = '사포상마장졸차'
    for i in range(len(en)):
        gib = gib.replace(en[i],ko[i])
    return gib

def parse_fen(fen):
    ranks = fen.split(' ')[0].split('/')
    board = []
    for rank in ranks:
        board_rank = []
        for char in rank:
            if char.isdigit():
                board_rank.extend([''] * int(char))
            else:
                board_rank.append(char)
        board.append(board_rank)
    return board

def gib_position(cp):
    cp = cp.lower().replace("eh","상마").replace("he","마상")
    kostr = re.sub(r"[^ㄱ-ㅣ가-힣]","",cp) # 한글만 남기기
    cp = f'[초차림 "{kostr[4:]}"]\n[한차림 "{kostr[:4]}"]'
    return cp

fen = 'reha1aehr/4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4/RHEA1AEHR'

board = parse_fen(en2ko(fen.upper()))

move = 'i3h3'#일단 예시로 하나만 들고 옴. ' '로 split하고 i%3!=0 나 '.' not in i 같은 걸로 거를 생각.
bp = move[:2]#전에 있던 좌표 before place
ap = move[-2:]#이동한 좌표 after place

def xy(t):
    return (10-int(t[1]))%10, s.index(t[0])

def movep(bp, ap):
    #if board(bp)!='':print(error)
    apx, apy = xy(ap)
    bpx, bpy = xy(bp)
    board[apx-1][apy] = board[bpx-1][bpy]
    board[bpx-1][bpy] = ''
    return f'{bpx}{bpy+1}{board[apx-1][apy]}{apx}{apy+1}'

'''
# Mapping dictionaries
abc = '0abcdefghi'
dic1 = {
    "대회명": "Event",
    "회전": "Round",
    "대국일자": "Date",
    "대국장소": "Site",
    "초대국자": "White",
    "한대국자": "Black",
    "제한시간": "TimeControl",
    '대국결과': "Result",
    "한 완승": "0-1",
    "초 완승": "1-0",
    "한 시간승": "0-1",
    "초 시간승": "1-0",
    "한 기권승": "0-1",
    "초 기권승": "1-0"
}
dic2 = {
    '초차림 "마상마상"': [1, "RHEA1AHER"],
    '한차림 "마상마상"': [0, "rhea1aher"],
    '초차림 "마상상마"': [1, "RHEA1AEHR"],
    '한차림 "마상상마"': [0, "rhea1aehr"],
    '초차림 "상마마상"': [1, "REHA1AHER"],
    '한차림 "상마마상"': [0, "reha1aher"],
    '초차림 "상마상마"': [1, "REHA1AEHR"],
    '한차림 "상마상마"': [0, "reha1aehr"]
}

def pgn_to_gib(pgn_data):
    lines = pgn_data.strip().split('\n')
    metadata = {}
    moves = []

    for line in lines:
        if line.startswith('['):
            key, value = line[1:-1].split(' ', 1)
            metadata[key] = value.strip('"')
        elif line[0].isdigit():
            moves.extend(line.split()[1::2])

    # Translate moves
    pgn_to_gib_coords = {
        'a': '0', 'b': '1', 'c': '2', 'd': '3', 'e': '4',
        'f': '5', 'g': '6', 'h': '7', 'i': '8', '0': '0',
        '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
        '6': '6', '7': '7', '8': '8', '9': '9'
    }

    gib_moves = []
    for move in moves:
        start = move[:2]
        end = move[2:]
        gib_move = f"{pgn_to_gib_coords[start[0]]}{pgn_to_gib_coords[start[1]]}{pgn_to_gib_coords[end[0]]}{pgn_to_gib_coords[end[1]]}"
        gib_moves.append(gib_move)

    # Construct GIB format
    gib_content = [
        f"[초차림 \"{metadata.get('Variant', '')}\"]",
        f"[한차림 \"{metadata.get('VariantFamily', '')}\"]"
    ]

    for i, move in enumerate(gib_moves, 1):
        gib_content.append(f"{i}. {move}")

    return "\n".join(gib_content)

def main(pgn_input_path, gib_output_path):
    try:
        with open(pgn_input_path, 'r') as file:
            pgn_data = file.read()
        gib_data = pgn_to_gib(pgn_data)
        with open(gib_output_path, 'w', encoding='utf-8') as file:
            file.write(gib_data)
        print(f"PGN to GIB conversion complete. Check the {gib_output_path} file.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
pgn_input_path = 'test.pgn'
gib_output_path = 'test.gib'
main(pgn_input_path, gib_output_path)
'''

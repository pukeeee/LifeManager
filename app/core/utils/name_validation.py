import re

emoji_specSign = re.compile(
    r'['
    r'\U0001F600-\U0001F64F'  # Эмодзи лиц
    r'\U0001F300-\U0001F5FF'  # Символы и пиктограммы
    r'\U0001F680-\U0001F6FF'  # Транспортные средства и символы
    r'\U0001F700-\U0001F77F'  # Алхимические символы
    r'\U0001F780-\U0001F7FF'  # Геометрические символы
    r'\U0001F800-\U0001F8FF'  # Дополнительные стрелки и символы
    r'\U0001F900-\U0001F9FF'  # Дополнительные эмодзи
    r'\U0001FA00-\U0001FA6F'  # Символы игр и спорта
    r'\U0001FA70-\U0001FAFF'  # Символы инструментов и принадлежностей
    r'\U00002702-\U000027B0'  # Разные символы
    r'\U000024C2-\U0001F251'  # Дополнительные символы
    r'\u200d'                 # Zero Width Joiner
    r'\u200c'                 # Zero Width Non-Joiner
    r'\u200b'                 # Zero Width Space
    r'\u200e'                 # Left-To-Right Mark
    r'\u200f'                 # Right-To-Left Mark
    r'\u202a-\u202e'          # Directional Formatting Characters
    r'\u2066-\u2069'          # Additional Directional Formatting Characters
    r'\u20d0-\u20ff'          # Combining Diacritical Marks for Symbols
    r'\u2e00-\u2e7f'          # Supplemental Punctuation
    r'\u3000-\u303f'          # CJK Symbols and Punctuation
    r'\uFE00-\uFE0F'          # Variation Selectors
    r'\uFE20-\uFE2F'          # Combining Half Marks
    r'\uFFF0-\uFFFF'          # Specials
    r']+'
)



letters = re.compile(r"^[a-zA-Zа-яА-ЯёЁіїєґІЇЄҐ']+$")



bad_words = [
    r"[хx][yу][йеёяю]",
    r"[пpn][иiі][зz][дd]",
    r"[еeё][б6b]",
    r"[б6b][lл][yaяя]",
    r"[пpn][иiіeеl][dд][aаиiіoеаоуя]",
    r"[gг][oо][vвb][nпн][oо]",
    r"[zз][aа][liл][yуu][pпn][aа]",
    r"[пpn][еeё][nпн][иiі][sсc]",
    r"[дdg][оo][лl][бb6][оoаa]",
    r"[вvbсc][ъь][еёe][вvbсc]"
    r"[sсc][еeё][хx]",
    r"[sсc][еeё][kк][sсc]",
    r"[пpn][иiіeе][sсc][uyюу][nпн]",
    r"[jж][oо][пpn]"
    r"[kкcс][yуu][nпн][иiіeе]"
    r"[аa][scс][scс]"
    r"[bvв][аa][grг][иiіeеln][nпн]"
    r"[dд][pрrг][oо][чc][h]"
    r"[sсc][oоaа][sсc]"
    r"[f][a][g]"
    r"[nнh][eiиі][gг][rрp]"
]
compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in bad_words]
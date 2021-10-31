from typing import Dict, List, Optional, Any, Union, Tuple

Word=str
StrId=int # Номер строки
WordId=int # Номер позиции в строке

class Position:
  str_pos:StrId
  word_pos:WordId
  def __init__(self,s,w):
    self.str_pos=s
    self.word_pos=w
  def __repr__(self)->str:
    return f"Position({self.str_pos},{self.word_pos})"
  def __eq__(self,other):
    return (self.str_pos,self.word_pos)==(other.str_pos,other.word_pos)
  def __lt__(self,other):
    return (self.str_pos,self.word_pos)<(other.str_pos,other.word_pos)
  def __le__(self,other):
    return self<other or self==other
  def __hash__(self):
    return hash(('Position',self.str_pos,self.word_pos))

class FileData:
  # Список строк файла
  lines:List[str]
  # Словарь следующих позиций слова к текущим позициям
  nexts:Dict[Optional[Position],Optional[Position]]
  # Словарь предыдущих позиций слова к текущим позициям
  prevs:Dict[Optional[Position],Optional[Position]]
  # Словарь слов от позиции начала слова
  words:Dict[Position,Word]
  def __init__(self,fname:str)->None:
    self.lines=list(open(fname).read().split('\n'))
    self.nexts={}
    self.prevs={}
    self.words={}
    oldstart=None
    for line_pos, line in enumerate(self.lines):
      for w,start,stop in str2words(line,line_pos,process_comments=False):
        self.words[start]=w
        self.nexts[oldstart]=start
        self.prevs[start]=oldstart
        oldstart=start
    self.nexts[oldstart]=None
    self.prevs[None]=start

# Группы символов. Считаем, что слова не могут состоять из символов,
# относящихся к разным группам.
GROUPS=[('\'"@_.,'
         '0123456789'
         'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
         'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя'),
        '&'
        '?'
        '[',
        ']',
        ';',
        '(',
        ')',
        '!-+/<>*=:']

def char2group(char:str)->int:
  assert len(char)==1
  for i,gi in enumerate(GROUPS):
    if char in gi:
      return i
  assert False, f"Character {char} doesn't belong to any group"
  return -1

def isspace(c:str)->bool:
  assert len(c)==1
  return c==' ' or c=='\t'

#  _   _      _                    __                  _   _
# | | | | ___| |_ __   ___ _ __   / _|_   _ _ __   ___| |_(_) ___  _ __
# | |_| |/ _ \ | '_ \ / _ \ '__| | |_| | | | '_ \ / __| __| |/ _ \| '_ \
# |  _  |  __/ | |_) |  __/ |    |  _| |_| | | | | (__| |_| | (_) | | | |
# |_| |_|\___|_| .__/ \___|_|    |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|
#              |_|


def str2words(s:str,
              linepos:StrId=0,
              process_comments:bool=False)->List[Tuple[Word,Position,Position]]:

  if not process_comments and s.startswith('--'):
    return []
  w1pos=Position(linepos,0)
  w2pos=Position(linepos,0)
  wstart:int=0
  curgroup:Optional[int]=None
  acc:list=[]
  def _addword(start,stop):
    nonlocal acc
    acc.append(
      (s[start:stop],Position(linepos,start),Position(linepos,stop)))
  for i,c in enumerate(s):
    ngroup=-1 if isspace(c) else char2group(c)
    if curgroup is not None:
      if ngroup!=curgroup:
        if curgroup!=-1:
          _addword(wstart,i)
        curgroup=ngroup
        wstart=i
    else:
      curgroup=ngroup
      wstart=i
  _addword(wstart,len(s))
  return acc


def strnum2words(str_pos:StrId,
                 fd:FileData,
                 **kwargs)->List[Tuple[Word,Position,Position]]:
  return str2words(fd.lines[str_pos], str_pos, **kwargs)

#  __  __       _         _____                 _   _
# |  \/  | __ _(_)_ __   |  ___|   _ _ __   ___| |_(_) ___  _ __  ___
# | |\/| |/ _` | | '_ \  | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | | (_| | | | | | |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
# |_|  |_|\__,_|_|_| |_| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/


FD=FileData('_sm234.vhd')

def find(word:Word, start_str:StrId, fd:FileData=FD)->Optional[Position]:
  """ Поиск слова в прямом направлении, начиная с данного номера строки """
  for nline in range(start_str,len(fd.lines)):
    for w,pos_start,pos_stop in strnum2words(nline,fd=fd):
      if w==word:
        return pos_start
  return None

def find_r(word:Word, start_str:StrId, fd:FileData=FD)->Optional[Position]:
  """ Поиск слова в обратном направлении, начиная с данного номера строки """
  for nline in reversed(range(0,start_str+1)):
    for w,pos_start,pos_stop in reversed(strnum2words(nline,fd=fd)):
      if w==word:
        return pos_start
  return None

def right_word(pos:Position, fd:FileData=FD)->Optional[Position]:
  return fd.nexts.get(pos,None)

def left_word(pos:Position, fd:FileData=FD)->Optional[Position]:
  return fd.prevs.get(pos,None)

def word_on_pos(pos:Position, fd:FileData=FD)->Optional[Word]:
  for k,v in fd.nexts.items():
    if k is not None and k<=pos and \
       (v is not None and v>pos) or (v is None):
      return fd.words[k]
  return None



#  _____         _
# |_   _|__  ___| |_ ___
#   | |/ _ \/ __| __/ __|
#   | |  __/\__ \ |_\__ \
#   |_|\___||___/\__|___/


teststr='aaa bbb ccc'
words=str2words(teststr)
assert ' '.join([w[0] for w in words])==teststr

for i,gi in enumerate(GROUPS):
  for j,gj in enumerate(GROUPS):
    if i!=j:
      assert set.intersection(set(gi),set(gj))==set(), \
        f"Duplicate symbol '{set.intersection(set(gi),set(gj))}'"

for l in FD.lines:
  for c in l:
    if not isspace(c):
      assert char2group(c)>=0

for k,v in FD.nexts.items():
  assert FD.prevs[v]==k
for k,v in FD.prevs.items():
  assert FD.nexts[v]==k




import operator
from RetrivalSys import DictBuild
from functools import cmp_to_key

class BTree(object):
  """具有插入、搜索、打印的B树。"""

  class Node(object):
      """B树的节点"""

      def __init__(self, t):
          self.keys = []
          self.children = []
          #是否为叶子节点
          self.leaf = True
          # t是树的度，节点的最大关键字数量是2t-1
          self._t = t

      def split(self, parent, payload):
          """分裂节点，调整key与children"""
          new_node = self.__class__(self._t)
          #_class_获得已有当前对象的类

          mid_point = self.size // 2
          #" / "表示 浮点数除法，返回浮点结果;" // "表示整数除法
          split_value = self.keys[mid_point]
          parent.add_key(split_value)

          # 将key与孩子节点添加到合适的节点
          new_node.children = self.children[mid_point + 1:]
          self.children = self.children[:mid_point + 1]
          # 将中间点之后的所有孩子节点赋给新的节点,[a:]表示将列表里a之后元素，[:a]表示列表里a之前的元素，包括a
          # 将中间点之前的所有孩子节点留给原节点
          new_node.keys = self.keys[mid_point + 1:]
          self.keys = self.keys[:mid_point]

          # 新节点有孩子，将它设为内节点
          if len(new_node.children) > 0:
              new_node.leaf = False

          parent.children = parent.add_child(new_node)
          #将key与提升的关键字比较，决定返回关键字应该插入的分支
          if cmp_precode(payload,split_value) is -1:
              return self
          else:
              return new_node

      @property
      def _is_full(self):
          return self.size == 2 * self._t - 1

      @property
      def size(self):
          return len(self.keys)

      def add_key(self, value):
          """
          将key的值为value添加keys列表
          """
          self.keys.append(value)
          self.keys.sort(key=cmp_to_key(cmp_precode), reverse=False) #对keys重新排序

      def add_child(self, new_node):
          """
          给节点添加一个孩子. 对节点的孩子节点重新排序. allowing for children
          to be ordered even after middle nodes are split.
          返回: 一个有序的孩子节点列表
          """
          i = len(self.children) - 1
          while i >= 0 and cmp_precode(self.children[i].keys[0],new_node.keys[0]) is 1:
              i -= 1
          return self.children[:i + 1] + [new_node] + self.children[i + 1:]

  def __init__(self, t):
    """
    Create the B-tree. t是树的度.（算法导论里的定义，度为内节点最少的孩子数目，所以每个节点最少有t个孩子，最少有t-1个key
    最多有2t个孩子，2t-1个key）Tree 刚建立时没有key
    允许重复的key
    """
    self._t = t
    if self._t <= 1:
      raise ValueError("B-Tree must have a degree of 2 or more.")
    self.root = self.Node(t)

  def insert(self, payload):
    """在B-Tree中插入值为payload的关键字"""
    node = self.root
    # 根节点比较特殊，需要单独定义
    if node._is_full:
      #根节点满，生成一个节点作为新的根节点，将原有根节点分裂为两个节点，作为孩子放入新的根节点孩子列表
      new_root = self.Node(self._t)
      new_root.children.append(self.root)
      new_root.leaf = False

      node = node.split(new_root, payload)
      self.root = new_root
    while not node.leaf:
      i = node.size - 1
      while i > 0 and cmp_precode(payload,node.keys[i]) is -1 :#找到key在当前node哪个key之间
        i -= 1
      if cmp_precode(payload,node.keys[i]) is 1:#在当前key的右分支
        i += 1

      next = node.children[i]
      if next._is_full:
        node = next.split(node, payload)
      else:
        node = next
    # 将路径上的所有满的节点都分裂，就可以轻松地插入key.
    node.add_key(payload)


  def search(self, value, node=None):
      """如果B树包含查询的key，返回node"""
      if node is None:
        node = self.root
      if node is not None:
          h = node.size
          i = 0
          while i < h:
              w = cmp_key(value, node.keys[i])
              if w is not -1 and w is not -2:
                  return w
              elif w is -2:
                  i +=1
              elif w is -1:
                  break
          if node.leaf:
              return False
          return self.search(value, node.children[i])
  '''
  def search(self, value, node=None):
    """如果B树包含查询的key，返回node"""
    if node is None:
      node = self.root
    if node is not None:
        h = node.size
        i = 0
        while i < h:
            w = cmp_key(value, node.keys[i])
            if w is not -1 and w is not -2:
                return w
            i +=1
        if node.leaf:
          #在叶节点中没有key，B树中不存在这个key
           return False
        else:
            # 比较key与当前节点keys中的大小，在孩子节点中递归寻找
            i = 0
            while i < node.size and cmp_key(value, node.keys[i]) is -2:
                i += 1
            return self.search(value, node.children[i])  
  '''

  def print_order(self):
    """按每层打印B树."""
    this_level = [self.root]
    while this_level:
      next_level = []
      output = ""
      for node in this_level:
        if node.children:
          next_level.extend(node.children)
        output += str(node.keys) + " "
      print(output)
      this_level = next_level

#比较压缩词典行precode1和precode2的关系
def cmp_precode(precode1, precode2):
      """前缀编码比较函数"""
      pre1 = precode1.split('*')[0]
      pre2 = precode2.split('*')[0]
      if pre1 == '':
          pre1 = DictBuild.LineDecompress(precode1)[0][0]
      if pre2 == '':
          pre2 = DictBuild.LineDecompress(precode2)[0][0]
      mlen = min(len(pre1),len(pre2))
      pre1 = pre1[0:mlen]
      pre2 = pre2[0:mlen]
      if operator.lt(pre1, pre2):
          return -1
      elif operator.gt(pre1, pre2):
          return 1

      elif operator.eq(pre1, pre2):
          word1 = DictBuild.LineDecompress(precode1)[0][0]
          word2 = DictBuild.LineDecompress(precode2)[0][0]
          if operator.lt(word1, word2):
              return -1
          elif operator.gt(word1, word2):
              return 1
          elif operator.eq(word1, word2):
              return 0


#单词比当前前缀小时，返回-1
#单词比当前前缀大时，返回-2
#找到时，返回偏移量
def cmp_key(key, precode):
    """key与前缀编码的比较函数"""
    pre = precode.split('*')[0]
    decode, offset = DictBuild.LineDecompress(precode)
    if pre == '':
        pre = decode[0]
    mlen = min(len(key), len(pre))
    prekey = key[0:mlen]
    pre = pre[0:mlen]
    if operator.lt(prekey, pre):
        if operator.ge(key, decode[0]):
            juge = find(decode, key)
            if juge is not -1:
                return offset[juge]
        return -1
    # key的前缀小于编码的前缀，key小于前缀
    elif operator.gt(prekey, pre):
        if operator.le(key, decode[len(decode) - 1]):
            juge = find(decode, key)
            if juge is not -1:
                return offset[juge]
        return -2
    elif operator.eq(pre, prekey):
        juge = find(decode, key)
        if juge is not -1:
            return offset[juge]
        elif operator.gt(key, decode[len(decode) - 1]):
            return -2
        elif operator.lt(key, decode[0]):
            return -1

def find(decode, key):
      """解码后，在块中二分查找"""
      low = 0
      high = len(decode) - 1
      while low <= high:
          mid = (low + high) // 2
          if operator.eq(decode[mid], key):
              return mid
          elif operator.gt(decode[mid], key):
              high = mid - 1
          elif operator.lt(decode[mid], key):
              low = mid + 1

      return -1

def FindWord(tree, word):

    #c.print_order()
    #print(c.search("A"))
    return tree.search(word)
#print(FindWord(2.5,"Call"))

'''
lists = open("./components/Drama/dict.txt", 'r')
w = open("./components/Drama/test.txt", 'w')
for line in lists:
    voclist = []
    offsets = []
    word = line.strip('\n').strip('{}').split(':')[0].strip('"')
    offset=FindWord(2.5, word)
    w.write(str(offset) + '\n')
lists.close()
w.close()
'''
def createTree(args, key=2.5):
    cpn_path = args.cpn_dir
    dict_path = cpn_path + 'CompressedDict.txt'
    c = BTree(key)
    dict_file = open(dict_path, "r", encoding="utf-8")
    for line in dict_file:
        line = line.strip('\n')
        c.insert(line)
    dict_file.close()
    return c

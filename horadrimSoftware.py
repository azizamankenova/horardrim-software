from collections import deque
import json
import os
from fileManager import FileReader
from constants import *

def binarySearch(array, first, last, x):
    if last == -1:
        return (False, 0)
    if last == first:
        if array[first] < x:
            return (False, first + 1)
        elif array[first] > x:
            return (False, first)
    mid = first + (last - first) // 2
    if x == array[mid]:
        return (True, mid)
    elif x > array[mid]:
        return binarySearch(array, mid + 1, last, x)
    else:
        return binarySearch(array, first, mid, x)

N = 3

class TreeNode:
    def __init__(self, isLeaf, parent=None):
        self.isLeaf = isLeaf
        self.keys = [] * N
        self.pointers = [] * N
        self.next = None
        self.prev = None
        self.parent = parent

class BPlusTree:
    def __init__(self, type):
        self.root = TreeNode(True)
        self.type = type
        self.order = N // 2
        self.loadTree()

    def search(self, key):
        node = self.root
        while True:
            found, index = binarySearch(node.keys, 0, len(node.keys) - 1, key)

            if not node.isLeaf:
                pointer = node.pointers[index if not found else index + 1]
                if pointer:
                    node = pointer
                    continue
            else:
                return (found, index, node)

    def insert(self, key, pointer):
        found, index, node = self.search(key)
        if found:
            print("Error")
        else:
            node.keys.insert(index, key)
            node.pointers.insert(index, pointer)

            if len(node.keys) == N:
                new_node = TreeNode(True, node.parent)
                mid = len(node.keys) // 2;
                new_node.keys = node.keys[mid:]
                new_node.pointers = node.pointers[mid:]
                node.keys = node.keys[:mid]
                node.pointers = node.pointers[:mid]
                new_node.next = node.next
                new_node.prev = node
                node.next = new_node
                if new_node.next:
                    new_node.next.prev = new_node

                def bubbleUp(old_node, new_node, new_key):
                    # if we are splitting root
                    if self.root == old_node:
                        self.root = TreeNode(False)
                        # mid remains in new_node ???
                        self.root.keys = [new_key]
                        self.root.pointers = [old_node, new_node]
                        old_node.parent = self.root
                        new_node.parent = self.root
                    else:
                        parent = old_node.parent
                        _, insert_index = binarySearch(parent.keys, 0, len(parent.keys) - 1, new_key)
                        parent.keys.insert(insert_index, new_key)
                        parent.pointers.insert(insert_index + 1, new_node)

                        if len(parent.keys) == N:
                            new_parent_node = TreeNode(False, parent.parent)
                            mid = len(parent.keys) // 2;
                            new_key = parent.keys[mid]
                            new_parent_node.keys = parent.keys[mid + 1:]
                            new_parent_node.pointers = parent.pointers[mid + 1:]
                            parent.keys = parent.keys[:mid]
                            parent.pointers = parent.pointers[:mid + 1]

                            new_parent_node.next = parent.next
                            new_parent_node.prev = parent
                            parent.next = new_parent_node
                            if new_parent_node.next:
                                new_parent_node.next.prev = new_parent_node

                            # necessary?
                            for pointer in parent.pointers:
                                pointer.parent = parent

                            for pointer in new_parent_node.pointers:
                                pointer.parent = new_parent_node

                            
                            bubbleUp(parent, new_parent_node, new_key)

                bubbleUp(node, new_node, new_node.keys[0])

            self.saveTree()

        # def delete(self, key):
        #     found, index, node = self.search(key)
        #     if not found:
        #         print("Error")
        #     else:
        #         node.keys.pop(index)
        #         node.pointers.pop(index)

        #         if len(node.keys) < N // 2:
        #             if node.prev and node.parent == node.prev.parent:
        #                 if len(node.prev.keys) > N // 2:
        #                     node.keys.insert(0, node.prev.keys.pop())
        #                     node.pointers.insert(0, node.prev.pointers.pop())
        #                 else:
        #                     node.keys.insert(0, node.prev.keys.pop())
        #                     node.pointers.insert(0, node.prev.pointers.pop())
        #                     parent = node.parent
        #                     for i, pointer in enumerate(parent.pointers):
        #                         if pointer == node.prev:
        #                             node.parent.keys[i] = node.next.keys[-1]
        #                             break
        #             elif node.next and node.parent == node.next.parent:
        #                 if len(node.next.keys) > N // 2:
        #                     node.keys.append(node.next.keys.pop(0))
        #                     node.pointers.append(node.next.pointers.pop(0))
        #                 else:
        #                     node.keys.append(node.next.keys.pop(0))
        #                     node.pointers.append(node.next.pointers.pop(0))
        #                     parent = node.parent
        #                     for i, pointer in enumerate(parent.pointers):
        #                         if pointer == node:
        #                             node.parent.keys[i] = node.next.keys[0]
        #                             break

        #         self.saveTree()

    def delete(self, parent, node, key, oldchild):
        found, index = binarySearch(node.keys, 0, len(node.keys) - 1, key)

        if not node.isLeaf:
            pointer = node.pointers[index if not found else index + 1]
            self.delete(node, pointer, key, oldchild)
            if not oldchild: 
                return
            
        if node.isLeaf:
            if len(node.keys) > self.order:
                if found:
                    node.keys.pop(index)
                    node.pointers.pop(index)
                else:
                    print("Error")
            else:
                if node.prev and node.parent == node.prev.parent:
                    M = node

                    if len(node.prev.keys) > N // 2:
                        node.keys.insert(0, node.prev.keys.pop())
                        node.pointers.insert(0, node.prev.pointers.pop())
                        parent = node.parent
                        for i, pointer in enumerate(parent.pointers):
                            if pointer == M:
                                node.parent.keys[i - 1] = M.keys[0]
                                break

                        oldchild = None      
                        return
                    else:
                        for i, pointer in enumerate(parent.pointers):
                            if pointer == M:
                                oldchild = node.parent.keys[i - 1]
                                break
                        

                elif node.next and node.parent == node.next.parent:                        
                    M = node.next

                    if len(node.next.keys) > N // 2:
                        node.keys.append(node.next.keys.pop(0))
                        node.pointers.append(node.next.pointers.pop(0))
                        parent = node.parent
                        for i, pointer in enumerate(parent.pointers):
                            if pointer == M:
                                node.parent.keys[i - 1] = M.keys[0]
                                break
                        
                        oldchild = None      
                        return
                    else:
                        for i, pointer in enumerate(parent.pointers):
                            if pointer == M:
                                oldchild = node.parent.keys[i - 1]
                                break
                        
                        node.keys += M.keys
                        node.pointers += M.pointers
                        del M



    def getNodesByLevel(self):
        result = []
        queue = deque()
        queue.append(self.root)

        while len(queue) > 0:
            levelSize = len(queue)
            level = []
            for _ in range(levelSize):
                node = queue.popleft()
                if type(node) is TreeNode:
                    level.append(node)
                    for pointer in node.pointers:
                        queue.append(pointer)
            result.append(level)

        return result[1:-1]
    
    def saveTree(self):
        tree_dict = self.serializeTree(self.root)
        os.makedirs("index", exist_ok=True)
        with open(os.path.join("index", f"{self.type}.json"), 'w') as f:
            json.dump(tree_dict, f)


    def serializeTree(self, node):
        tree_dict = {
            "isLeaf": node.isLeaf,
            "keys": node.keys,
            "pointers": []
        }

        for pointer in node.pointers:
            if type(pointer) is TreeNode:
                tree_dict["pointers"].append(self.serializeTree(pointer))
            else:
                tree_dict["pointers"].append(pointer)

        return tree_dict

    def deserializeTree(self, tree_dict):
        node = TreeNode(tree_dict["isLeaf"])
        node.keys = tree_dict["keys"]
        node.pointers = tree_dict["pointers"]

        for pointer in node.pointers:
            if type(pointer) is dict:
                node.pointers[node.pointers.index(pointer)] = self.deserializeTree(pointer)

        return node

    def loadTree(self):
        os.makedirs("index", exist_ok=True)
        path = os.path.join("index", f"{self.type}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                tree_dict = json.load(f)
                self.root = self.deserializeTree(tree_dict)
                self.connectTree()

    def connectTree(self):
        queue = deque()
        queue.append(self.root)

        while len(queue) > 0:
            levelSize = len(queue)
            level = []
            for _ in range(levelSize):
                node = queue.popleft()
                level.append(node)
                for pointer in node.pointers:
                    if type(pointer) is TreeNode:
                        pointer.parent = node
                        queue.append(pointer)

            self.connectNodes(level)

    def connectNodes(self, level):
        for i in range(len(level) - 1):
            level[i].next = level[i + 1]
            level[i + 1].prev = level[i]

    def getAllRecords(self):
        node = self.root
        records = []

        if not node.isLeaf:
            while not node.isLeaf:
                node = node.pointers[0]
            while node.next:
                for pointer in node.pointers:
                    records.append(pointer)
                node = node.next
        else:
            records = node.pointers

        records_ascending = []
        for record in records:
            [fileName, pageIndex, recordIndex] = record
            fileReader = FileReader(os.path.join("data", self.type, fileName))
            page = fileReader.readPage(pageIndex)
            record = page[PAGE_HEADER + recordIndex * RECORD_SIZE : PAGE_HEADER + (recordIndex+1) * RECORD_SIZE]
            records_ascending.append(" ".join(record.split()))
        
        return records_ascending

    def filter(self, type, key, value, sign):
        found, index, node = self.search(value)
        records = []
        if sign == '>':
            if found:
                index = index + 1
            while index < len(node.keys):
                records.append(node.pointers[index])
                index = index + 1
            while node.next:
                for pointer in node.next.pointers:
                    records.append(pointer)
                node = node.next
               
        elif sign == '<':
            index = index - 1
            while index >= 0:
                records.append(node.pointers[index])
                index = index - 1
            while node.prev:
                for pointer in node.prev.pointers:
                    records.append(pointer)
                node = node.prev
        else:
            if found:
                records.append(node.pointers[index])    
            else:
                print('error')        
        
        records_ascending = []
        for record in records:
            [fileName, pageIndex, recordIndex] = record
            fileReader = FileReader(os.path.join("data", self.type, fileName))
            page = fileReader.readPage(pageIndex)
            record = page[PAGE_HEADER + recordIndex * RECORD_SIZE : PAGE_HEADER + (recordIndex+1) * RECORD_SIZE]
            records_ascending.append(" ".join(record.split()))

        return records_ascending
       

        



# tree = BPlusTree("angel")
# tree.insert(1, "1")
# tree.insert(2, "2")
# tree.insert(3, "3")
# tree.insert(4, "4")
# tree.insert(5, "5")
# tree.insert(6, "6")
# tree.insert(7, "7")
# tree.insert(8, "8")
# tree.saveTree()

# tree = BPlusTree("angel")
# tree.loadTree()
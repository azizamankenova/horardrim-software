import os
import shutil
from bplustree import BPlusTree, indeces
from storageManager import StorageManager
from systemCatalogue import SystemCatalogue
from fileManager import FileReader
from constants import *

def findTree(type):
    tree = None
    if type in indeces:
        tree = indeces[type]
    else:
        tree = BPlusTree(type)
        indeces[type] = tree

    return tree

class DefinitionLanguageOperations:
    @staticmethod
    def createType(type, fields):
        if os.path.exists(os.path.join("data", type)):
            return False
        else:
            StorageManager.createPageData(type)
            StorageManager.createFile(type)
            SystemCatalogue.addType(fields)
            return True
    
    @staticmethod
    def deleteType(type):
        path = os.path.join("data", type)
        if os.path.exists(path):
            shutil.rmtree(path)
            os.remove(os.path.join("index", f"{type}.json"))
            SystemCatalogue.deleteType(type)
            return True
        else:
            return False

    @staticmethod
    def listType():
        return os.listdir("data")

    @staticmethod
    def createRecord(type, fields):
        tree = findTree(type)
        fields = SystemCatalogue.transformFields(type, fields)
        pkey = SystemCatalogue.getPrimaryKey(type, fields)
        if tree.query(pkey):
            return False

        path = os.path.join("data", type)
        if os.path.exists(path):
            emptyPage = StorageManager.findEmptyPage(type)
            if not emptyPage:
                StorageManager.createFile(type)
                emptyPage = StorageManager.findEmptyPage(type)
            reader = FileReader(os.path.join("data", type, emptyPage['file']))
            page = reader.readPage(emptyPage['page'])

            field_str = "{:<240}".format("".join(["{:<20}".format(field) for field in  fields]))
           
            for i in range(NUM_RECORDS):
                if page[i] == '0':
                    record_location = [emptyPage['file'], emptyPage['page'], i]
                    reader.writeRecord(emptyPage['page'], i, field_str)
                    tree[pkey] = record_location
                    break       

            return True
            
        else:
            return False

    @staticmethod
    def searchRecord(type, pkey):
        tree = findTree(type) 
            
        found, index, node = tree.search(pkey)
        if found:
            [fileName, pageIndex, recordIndex] = node.values[index]
            fileReader = FileReader(os.path.join("data", type, fileName))
            page = fileReader.readPage(pageIndex)
            record = page[PAGE_HEADER + recordIndex * RECORD_SIZE : PAGE_HEADER + (recordIndex+1) * RECORD_SIZE]
            return " ".join(record.split())
        else:
            return False

    @staticmethod
    def updateRecord(type, pkey, fields):
        tree = findTree(type)
        found, index, node = tree.search(pkey)
        if found:
            [fileName, pageIndex, recordIndex] = node.values[index]
            fileReader = FileReader(os.path.join("data", type, fileName))
            field_str = "{:<240}".format("".join(["{:<20}".format(field) for field in fields]))
            fileReader.writeRecord(pageIndex, recordIndex, field_str)
            return True
        else:
            return False

    @staticmethod
    def listRecord(type):
        tree = findTree(type)
        return tree.getAllRecords()

    @staticmethod
    def filterRecord(type, pkey, value, sign):
        tree = findTree(type)
        pkey_type = SystemCatalogue.getFields(type)[0]["type"]
        if pkey_type == 'int':
            value = int(value)
        return tree.filter(type, pkey, value, sign)

    @staticmethod
    def deleteRecord(type, pkey):
        tree = findTree(type)
        if tree.deleteKey(type, pkey):
            return True






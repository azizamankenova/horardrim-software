import os
from definitionLanguage import DefinitionLanguageOperations
from systemCatalogue import SystemCatalogue
import time
import csv
from bplustree import indeces

if not os.path.exists("SystemCatalogue.csv"):
    SystemCatalogue.initialize()

with open('input_1.txt') as file:
    lines = [line.rstrip() for line in file]

    with open("horadrimLog.csv", "a", newline='') as f:
        writer = csv.writer(f)

        def log(line, isCreated):
            writer.writerow([int(time.time()), line, 'success' if isCreated else 'failure'])

        for line in lines:
            words = line.split()
            if words[0] == 'create' and words[1] == 'type':
                type_name = words[2]
                num_fields = words[3]
                pkey = int(words[4])
                fields = words[5:]
                rows = [] 
                for position, (name, type) in enumerate(zip(*[iter(fields)] * 2)):
                    if position + 1 != pkey:
                        rows.append([type_name, position, name, type])
                    else:
                        rows.insert(0, [type_name, position, name, type])

                isCreated = DefinitionLanguageOperations.createType(type_name, rows)
                log(line, isCreated)
            elif words[0] == 'delete' and words[1] == 'type':
                type = words[2]
                isDeleted = DefinitionLanguageOperations.deleteType(type)
                log(line, isDeleted)
            elif words[0] == 'list' and words[1] == 'type':
                types = DefinitionLanguageOperations.listType()
                isListed = False
                if types:
                    isListed = True
                    for type in types:
                        print(type)
                log(line, isListed)
            elif words[0] == 'create' and words[1] == 'record':
                type = words[2]
                field_values = words[3:]
                isCreated = DefinitionLanguageOperations.createRecord(type, field_values)
                log(line, isCreated)
            elif words[0] == 'delete' and words[1] == 'record':
                type = words[2]
                pkey = words[3]
                isDeleted = DefinitionLanguageOperations.deleteRecord(type, pkey)
                log(line, isDeleted)
            elif words[0] == 'update':
                type = words[2]
                pkey = words[3]
                field_values = words[4:]
                isUpdated = DefinitionLanguageOperations.updateRecord(type, pkey, field_values)
                log(line, isUpdated)
            elif words[0] == 'search':
                type = words[2]
                pkey = words[3]
                field = DefinitionLanguageOperations.searchRecord(type, pkey)
                found = False
                if field:
                    print(field)
                    found = True
                log(line, found)
                
            elif words[0] == 'list' and words[1] == 'record':
                type = words[2]
                records = DefinitionLanguageOperations.listRecord(type)
                isListed = False
                if records:
                    isListed = True
                    for record in records:
                        print(record)
                log(line, isListed)
            elif words[0] == 'filter':
                type = words[2]
                condition = words[3]

                selected = ""
                if '>' in condition:
                    selected = '>'
                elif '<' in condition:
                    selected = '<'
                elif '=' in condition:
                    selected = '='

                field_name, value = condition.split(selected)
                records = DefinitionLanguageOperations.filterRecord(type, field_name, value, selected)
                isFiltered = False
                if records:
                    isFiltered = True
                    for record in records:
                        print(record)
                log(line, isFiltered)


for tree in list(indeces.values()):
    tree.saveTree()
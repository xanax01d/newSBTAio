from .groups import groupList
from .databaseTables import tableList
from .googleTableKeys import keysList

groupsToTables = dict(zip(groupList,tableList))
tablesToKeys = dict(zip(tableList,keysList))
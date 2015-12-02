import httplib
import json
import models

"""
Helper Method used to get all data from request string.
"""
def RetrieveData(request):
  connection = httplib.HTTPConnection("https://visualgenome.org", '443')
	connection.request("GET", request)
	response = connection.getresponse()
	jsonString = response.read()
	data = json.loads(jsonString)
  return data

"""
Get all Image ids.
"""
def GetAllImageIds():
  next = '/api/v0/images/all?page=1' 
  ids = []
  while next is not None:
    data = RetrieveData(next.replace('https://visualgenome.org:443', ''))
    ids.extend(data['results'])
    next = data['next']
  return ids

"""
Get Image ids from startIndex to endIndex.
"""
def GetImageIdsInRange(startIndex=0, endIndex=99):
  idsPerPage = 100
  startPage = startIndex / idsPerPage + 1
  endPage = endIndex / idsPerPage + 1
  ids = []
  for page in range(startPage, endPage+1):
    data = RetrieveData('/api/v0/images/all?page=' + page)
    ids.extend(data['results'])
  ids = ids[startIndex % 100:]
  ids = ids[:endIndex-startIndex+1]
  return ids


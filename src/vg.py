import httplib
import json
from models import Image, Object, Attribute, Relationship
from models import Region, Graph, QA, QAObject, Synset

#=================== Helper Methods ===============================
"""
Helper Method used to get all data from request string.
"""
def RetrieveData(request):
  connection = httplib.HTTPSConnection("visualgenome.org", '443')
  #connection = httplib.HTTPConnection("localhost", '8000')
  connection.request("GET", request)
  response = connection.getresponse()
  jsonString = response.read()
  data = json.loads(jsonString)
  return data

"""
Helper to Extract Synset from canon object.
"""
def ParseSynset(canon):
  if len(canon) == 0:
    return None
  return Synset(canon[0]['synset_name'], canon[0]['synset_definition'])

"""
Helper to parse a Graph object from API data.
"""
def ParseGraph(data, image):
  objects = []
  object_map = {}
  relationships = []
  attributes = []
  # Create the Objects
  for obj in data['bounding_boxes']:
    names = []
    synsets = []
    for s in obj['boxed_objects']:
      names.append(s['name'])
      synsets.append(ParseSynset(s['object_canon']))
      object_ = Object(obj['id'], obj['x'], obj['y'], obj['width'], obj['height'], names, synsets)
      object_map[obj['id']] = object_
    objects.append(object_)
  # Create the Relationships
  for rel in data['relationships']:
    relationships.append(Relationship(rel['id'], object_map[rel['subject']], \
        rel['predicate'], object_map[rel['object']], ParseSynset(rel['relationship_canon'])))
  # Create the Attributes
  for atr in data['attributes']:
    attributes.append(Attribute(atr['id'], object_map[atr['subject']], \
        atr['attribute'], ParseSynset(atr['attribute_canon'])))
  return Graph(image, objects, relationships, attributes)


#=================== API Calls =====================================
"""
Get all Image ids.
"""
def GetAllImageIds():
  page = 1
  next = '/api/v0/images/all?page=' + str(page)
  ids = []
  while True:
    data = RetrieveData(next)
    ids.extend(data['results'])
    if data['next'] is None:
      break
    page += 1
    next = '/api/v0/images/all?page=' + str(page)
  return ids

"""
Get Image ids from startIndex to endIndex.
"""
def GetImageIdsInRange(startIndex=0, endIndex=99):
  idsPerPage = 1000
  startPage = startIndex / idsPerPage + 1
  endPage = endIndex / idsPerPage + 1
  ids = []
  for page in range(startPage, endPage+1):
    data = RetrieveData('/api/v0/images/all?page=' + str(page))
    ids.extend(data['results'])
  ids = ids[startIndex % 100:]
  ids = ids[:endIndex-startIndex+1]
  return ids

"""
Get data about an image.
"""
def GetImageData(id=61512):
  data = RetrieveData('/api/v0/images/' + str(id))
  if 'detail' in data and data['detail'] == 'Not found.':
    return None
  url = data['url']
  width = data['width']
  height = data['height']
  coco_id = data['coco_id']
  flickr_id = data['flickr_id']
  image = Image(id, url, width, height, coco_id, flickr_id)
  return image	

"""
Get the region descriptions of an image.
"""
def GetRegionDescriptionsOfImage(id=61512):
  image = GetImageData(id=id)
  data = RetrieveData('/api/v0/images/' + str(id) + '/regions')
  if 'detail' in data and data['detail'] == 'Not found.':
    return None
  regions = []
  for d in data:
    regions.append(Region(d['id'], image, d['phrase'], d['x'], d['y'], d['width'], d['height']))
  return regions

"""
Get Region Graph of a particular Region in an image.
"""
def GetRegionGraphOfRegion(image_id=61512, region_id=1):
  image = GetImageData(id=image_id)
  data = RetrieveData('/api/v0/images/' + str(image_id) + '/regions/' + str(region_id))
  if 'detail' in data and data['detail'] == 'Not found.':
    return None
  return ParseGraph(data[0], image)

"""
Get Scene Graph of an image.
"""
def GetSceneGraphOfImage(id=61512):
  image = GetImageData(id=id)
  data = RetrieveData('/api/v0/images/' + str(id) + '/graph')
  if 'detail' in data and data['detail'] == 'Not found.':
    return None
  return ParseGraph(data, image)

"""
Gets all the QA from the dataset.
qtotal    int       total number of QAs to return. Set to None if all QAs should be returned
"""
def GetAllQAs(qtotal=100):
  page = 1
  next = '/api/v0/qa/all?page=' + str(page)
  qas = []
  image_map = {}
  while True:
    data = RetrieveData(next)
    for d in data['results']:
      if d['image'] not in image_map:
        image_map[d['image']] = GetImageData(id=d['image'])
      qos = []
      aos = []
      if 'question_objects' in d:
        for qo in d['question_objects']:
          synset = Synset(qo['synset_name'], qo['synset_definition'])
          qos.append(QAObject(qo['entity_idx_start'], qo['entity_idx_end'], qo['entity_name'], synset))
      if 'answer_objects' in d:
        for ao in d['answer_objects']:
          synset = Synset(o['synset_name'], ao['synset_definition'])
          aos.append(QAObject(ao['entity_idx_start'], ao['entity_idx_end'], ao['entity_name'], synset))
      qas.append(QA(d['id'], image_map[d['image']], d['question'], d['answer'], qos, aos))
      if qtotal is not None and len(qas) > qtotal:
        return qas
    if data['next'] is None:
      break
    page += 1
    next = '/api/v0/qa/all?page=' + str(page)
  return qas

"""
Get all QA's of a particular type - example, 'why'
qtype     string    possible values: what, where, when, why, who, how.
qtotal    int       total number of QAs to return. Set to None if all QAs should be returned
"""
def GetQAofType(qtype='why', qtotal=100):
  page = 1
  next = '/api/v0/qa/' + qtype + '?page=' + str(page)
  qas = []
  image_map = {}
  while True:
    data = RetrieveData(next)
    for d in data['results']:
      if d['image'] not in image_map:
        image_map[d['image']] = GetImageData(id=d['image'])
      qos = []
      aos = []
      if 'question_objects' in d:
        for qo in d['question_objects']:
          synset = Synset(qo['synset_name'], qo['synset_definition'])
          qos.append(QAObject(qo['entity_idx_start'], qo['entity_idx_end'], qo['entity_name'], synset))
      if 'answer_objects' in d:
        for ao in d['answer_objects']:
          synset = Synset(o['synset_name'], ao['synset_definition'])
          aos.append(QAObject(ao['entity_idx_start'], ao['entity_idx_end'], ao['entity_name'], synset))
      qas.append(QA(d['id'], image_map[d['image']], d['question'], d['answer'], qos, aos))
      if qtotal is not None and len(qas) > qtotal:
        return qas
    if data['next'] is None:
      break
    page += 1
    next = '/api/v0/qa/' + qtype + '?page=' + str(page)
  return qas

"""
Get all QAs for a particular image.
"""
def GetQAofImage(id=61512):
  page = 1
  next = '/api/v0/image/' + str(id) + '/qa?page=' + str(page)
  qas = []
  image_map = {}
  while True:
    data = RetrieveData(next)
    for d in data['results']:
      if d['image'] not in image_map:
        image_map[d['image']] = GetImageData(id=d['image'])
      qos = []
      aos = []
      if 'question_objects' in d:
        for qo in d['question_objects']:
          synset = Synset(qo['synset_name'], qo['synset_definition'])
          qos.append(QAObject(qo['entity_idx_start'], qo['entity_idx_end'], qo['entity_name'], synset))
      if 'answer_objects' in d:
        for ao in d['answer_objects']:
          synset = Synset(o['synset_name'], ao['synset_definition'])
          aos.append(QAObject(ao['entity_idx_start'], ao['entity_idx_end'], ao['entity_name'], synset))
      qas.append(QA(d['id'], image_map[d['image']], d['question'], d['answer'], qos, aos))
    if data['next'] is None:
      break
    page += 1
    next = '/api/v0/image/' + str(id) + '/qa?page=' + str(page)
  return qas



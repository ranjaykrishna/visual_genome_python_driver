import httplib
import json

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

"""
Helper to parse the image data for one image.
"""
def ParseImageData(data):
  url = data['url']
  width = data['width']
  height = data['height']
  coco_id = data['coco_id']
  flickr_id = data['flickr_id']
  image = Image(id, url, width, height, coco_id, flickr_id)
  return image	

"""
Helper to parse region descriptions.
"""
def ParseRegionDescriptions(data):
  regions = []
  for d in data:
    regions.append(Region(d['id'], image, d['phrase'], d['x'], d['y'], d['width'], d['height']))
  return regions



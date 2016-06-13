from models import Image, Object, Attribute, Relationship
from models import Region, Graph, QA, QAObject, Synset
import httplib
import json
import utils
import os

"""
Get Image ids from startIndex to endIndex.
"""
def GetAllImageData(dataDir=None):
  if dataDir is None:
    dataDir = utils.GetDataDir()
  dataFile = os.path.join(dataDir, 'image_data.json')
  data = json.load(open(dataFile))
  return [utils.ParseImageData(image) for image in data]

"""
Get all region descriptions.
"""
def GetAllRegionDescriptions(dataDir=None):
  if dataDir is None:
    dataDir = utils.GetDataDir()
  dataFile = os.path.join(dataDir, 'region_descriptions.json')
  imageData = GetAllImageData(dataDir)
  imageMap = {}
  for d in imageData:
    imageMap[d.id] = d
  images = json.load(open(dataFile))
  output = []
  for image in images:
    output.append(utils.ParseRegionDescriptions(image['regions'], imageMap[image['id']]))
  return output


"""
Get all question answers.
"""
def GetAllQAs(dataDir=None):
  if dataDir is None:
    dataDir = utils.GetDataDir()
  dataFile = os.path.join(dataDir, 'question_answers.json')
  imageData = GetAllImageData(dataDir)
  imageMap = {}
  for d in imageData:
    imageMap[d.id] = d
  images = json.load(open(dataFile))
  output = []
  for image in images:
    output.append(utils.ParseQA(image['qas'], imageMap))
  return output


"""
Convert list of objects with `id` attribute to dictionary indexing objects by id.

"""
def ListToDict(ls):
  return {obj.id:obj for obj in ls}


"""
Get all scene graphs.

"""
def GetAllSceneGraphs(dataDir='data/', imageDataDir='data/by-id/'):
  images = ListToDict(GetAllImageData(dataDir))
  scene_graphs = []

  for fname in os.listdir(imageDataDir):
    image_id = fname.split('.')[0]
    image = images[image_id]
    data = json.load(open(imageDataDir + fname, 'r'))

    scene_graph = ParseGraphLocal(data, image)
    scene_graphs.append(scene_graph)

  return scene_graphs


def GetSceneGraphs(image_id, images='data/', imageDataDir='data/by-id/'):
  if type(images) is str:
    images = ListToDict(GetAllImageData(images))

  fname = str(image_id) + '.json'
  image = images[image_id]
  data = json.load(open(imageDataDir + fname, 'r'))

  scene_graph = ParseGraphLocal(data, image)
  return scene_graph




"""
Save a unique json file for each image id; required for GetSceneGraphs.

Each json has the following keys:
  - 'id'
  - 'attributes'
  - 'objects'
  - 'relationships'

"""
def SaveById(dataDir='data/', imageDataDir='data/by-id/'):
  import gc
  if not os.path.exists(imageDataDir): os.mkdir(imageDataDir)

  fnames = ['attributes','objects','relationships']
  for fname in fnames:

    with open(dataDir + fname + '.json', 'r') as f:
      a = json.load(f)

    for item in a:
      iid = item['id']
      ifname = imageDataDir + str(iid) + '.json'

      if os.path.exists(ifname):
        with open(ifname, 'r') as f:
          data = json.load(f)
      else:
        data = {'id' : iid}

      data[fname] = item[fname]
      with open(ifname, 'w') as f:
        json.dump(data, f)

    del a
    gc.collect()

"""
Modified version of `utils.ParseGraph`.

  Note: synset data for objects is not provided in the downloadable .json files

"""
def ParseGraphLocal(data, image):
  objects = []
  object_map = {}
  relationships = []
  attributes = []
  # Create the Objects
  for obj in data['objects']:
    object_ = Object(obj['id'], obj['x'], obj['y'], obj['w'], obj['h'], obj['names'], [])
    object_map[obj['id']] = object_
    objects.append(object_)
  # Create the Relationships
  for rel in data['relationships']:
    relationships.append(Relationship(rel['id'], object_map[rel['subject']], \
        rel['predicate'], object_map[rel['object']], []))
  # Create the Attributes
  for atr in data['attributes']:
    attributes.append(Attribute(atr['id'], object_map[atr['subject']], \
        atr['attribute'], []))
  return Graph(image, objects, relationships, attributes)


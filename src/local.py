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
Load a single scene graph from a .json file.
"""
def GetSceneGraph(image_id, images='data/', imageDataDir='data/by-id/'):
  if type(images) is str:
    images = ListToDict(GetAllImageData(images))

  fname = str(image_id) + '.json'
  image = images[image_id]
  data = json.load(open(imageDataDir + fname, 'r'))

  scene_graph = ParseGraphLocal(data, image)
  return scene_graph

"""
Get scene graphs given locally stored .json files; requires `SaveSceneGraphsById`.

startIndex, endIndex : get scene graphs listed by image, from startIndex through endIndex
dataDir : directory with `image_data.json`
imageDataDir : directory of scene graph jsons by image id; see `SaveSceneGraphsById`
minRels, maxRels: only get scene graphs with at least / less than this number of relationships
"""
def GetSceneGraphs(startIndex=0, endIndex=-1, 
                   dataDir='data/', imageDataDir='data/by-id/',
                   minRels=1, maxRels=100):
  images = ListToDict(GetAllImageData(dataDir))
  scene_graphs = []

  img_fnames = os.listdir(imageDataDir)
  if (endIndex < 1): endIndex = len(img_fnames)

  for fname in img_fnames[startIndex : endIndex]:
    image_id = int(fname.split('.')[0])
    scene_graph = GetSceneGraph(image_id, images, imageDataDir)
    n_rels = len(scene_graph.relationships)
    if (minRels <= n_rels <= maxRels):
      scene_graphs.append(scene_graph)

  return scene_graphs

"""
Save a separate .json file for each image id in `imageDataDir`.

Notes
-----
- Required for `GetSceneGraphs`, which loads all scene graph info for
  a subset of all scene graphs.
- `imageDataDir` will fill about 1.1G of space on disk
- `dataDir` is assumed to contain `objects.json`, `attributes.json`,
  and `relationships.json`

Each output .json has the following keys:
  - "id"
  - "attributes"
  - "objects"
  - "relationships"
"""
def SaveSceneGraphsById(dataDir='data/', imageDataDir='data/by-id/'):
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
        data = {'id':iid}
      data[fname] = item[fname]
      with open(ifname, 'w') as f:
        json.dump(data, f)

    del a
    gc.collect()  # clear memory


def MapObject(object_map, obj):
  oid = obj['id']
  if oid in object_map:
    object_ = object_map[obj['id']]
  else:
    names = obj['names'] if 'names' in obj else [obj['name']]
    object_ = Object(obj['id'], obj['x'], obj['y'], obj['w'], obj['h'], names, [])
    object_map[obj['id']] = object_
  return object_map, object_


"""
Modified version of `utils.ParseGraph`.

Note
----
- synset data for objects is not provided in the downloadable .json files, so synset
  is not included in the loaded Object, Relationship, and Attribute objects
- attribute json data does not give full object, only `object names` string,
  so Attribute objects do not link to Object objects
"""
def ParseGraphLocal(data, image):
  objects = []
  object_map = {}
  relationships = []
  attributes = []
  for obj in data['objects']:
    object_map, o_ = MapObject(object_map, obj)
    objects.append(o_)
  for rel in data['relationships']:
    object_map, s = MapObject(object_map, rel['subject'])
    v = rel['predicate']
    object_map, o = MapObject(object_map, rel['object'])
    relationships.append(Relationship(rel['id'], s, v, o, []))
  for atr in data['attributes']:
    s = atr['object_names'][0]
    for a in atr['attributes']:
      attributes.append(Attribute(atr['id'], s, a, []))
  return Graph(image, objects, relationships, attributes)

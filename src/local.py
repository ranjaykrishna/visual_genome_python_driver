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






# ----------------------------------------------------------------------------------------------------------------------
# Fix words, prune bad objs/rels; filter words using dicts in `GetSceneGraphsModified`
# ----------------------------------------------------------------------------------------------------------------------



def fix_words(sg, obj_words, rel_words, obj_filter, rel_filter):
    fix = lambda s: s.lower().strip().replace(' ','_')
    rename = lambda w, d: d[fix(w)] if fix(w) in d else fix(w)

    for j, r in enumerate(sg.relationships):
        s = rename(r.subject.names[0], obj_words)
        v = rename(r.predicate,        rel_words)
        o = rename(r.object.names[0],  obj_words)
        if (s not in obj_filter) or (v not in rel_filter) or (o not in obj_filter):
            sg.relationships[j] = None
        else:
            sg.relationships[j].subject.names[0] = s
            sg.relationships[j].predicate        = v
            sg.relationships[j].object.names[0]  = o
    sg.relationships = [r for r in sg.relationships if r is not None]

    for j, o in enumerate(sg.objects):
        o_ = rename(o.names[0], [])
        if o_ not in obj_filter:
            sg.objects[j] = None
        else:
            sg.objects[j].names[0] = o_
    sg.objects = [o for o in sg.objects if o is not None]

    if len(sg.objects) == 0 or len(sg.relationships) == 0:
        del sg
        return []
    else:
        return [sg]


"""
Get scene graphs given locally stored .json files; requires `SaveSceneGraphsById`.

startIndex, endIndex : get scene graphs listed by image, from startIndex through endIndex
dataDir : directory with `image_data.json`
imageDataDir : directory of scene graph jsons by image id; see `SaveSceneGraphsById`
minRels, maxRels: only get scene graphs with at least / less than this number of relationships
"""
def GetSceneGraphsModified(startIndex=0, endIndex=-1,
                           dataDir='data/', imageDataDir='data/by-id/',
                           minRels=1, maxRels=100,
                           oword_fname='data/pk/obj_words.pk', rword_fname='data/pk/rel_words.pk',
                           ofilter_fname='data/pk/obj_counts.pk', rfilter_fname='data/pk/rel_counts.pk'):
  images = ListToDict(GetAllImageData(dataDir))
  scene_graphs = []

  img_fnames = os.listdir(imageDataDir)
  if (endIndex < 1): endIndex = len(img_fnames)

  import pickle
  obj_words = pickle.load(open(oword_fname,'r'))
  rel_words = pickle.load(open(rword_fname,'r'))
  obj_filter = pickle.load(open(ofilter_fname,'r'))
  rel_filter = pickle.load(open(rfilter_fname,'r'))

  for fname in img_fnames[startIndex : endIndex]:
    image_id = int(fname.split('.')[0])
    scene_graph = GetSceneGraph(image_id, images, imageDataDir)
    n_rels = len(scene_graph.relationships)
    if (minRels <= n_rels <= maxRels):
      scene_graphs += fix_words(scene_graph, obj_words, rel_words, obj_filter, rel_filter)

  return scene_graphs


# ----------------------------------------------------------------------------------------------------------------------
# For loading VRD dataset
# ----------------------------------------------------------------------------------------------------------------------



import simplejson
def GetSceneGraphsVRD(json_file='data/vrd/test.json', minRels=1, maxRels=100):
  scene_graphs = []
  with open(json_file,'r') as f:
    D = simplejson.load(f)

  scene_graphs = [ParseGraphVRD(d) for d in D]
  return scene_graphs


def ParseGraphVRD(d):
  image = Image(data['photo_id'], data['filename'], data['width'], data['height'], '', '')

  id2obj = {}
  objs = []
  rels = []
  atrs = []

  for i,o in enumerate(d['objects']):
    b = o['bbox']
    obj = Object(i, b['x'], b['y'], b['w'], b['h'], o['names'], [])
    id2obj[i] = obj
    objs.append(obj)

    for j,a in enumerate(data['attributes']):
      atrs.append(Attribute(j, obj, a['attribute'], []))

  for i,r in enumerate(data['relationships']):
    s = id2obj[r['objects'][0]]
    o = id2obj[r['objects'][1]]
    v = r['relationship']
    rels.append(Relationship(i, s, v, o, []))

  return Graph(image, objs, relationships, atrs)

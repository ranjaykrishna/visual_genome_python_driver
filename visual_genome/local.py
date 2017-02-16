from models import Image, Object, Attribute, Relationship
from models import Region, Graph, QA, QAObject, Synset
import httplib
import ijson
import json
import utils
import os, gc

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
                   minRels=0, maxRels=100):
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
Use object ids as hashes to `src.models.Object` instances. If item not
  in table, create new `Object`. Used when building scene graphs from json.
"""
def MapObject(object_map, obj):

  oid = obj['object_id']
  obj['id'] = oid
  del obj['object_id']

  if oid in object_map:
    object_ = object_map[oid]

  else:
    if 'attributes' in obj:
      attrs = obj['attributes']
      del obj['attributes']
    else:
      attrs = []
    if 'w' in obj:
      obj['width'] = obj['w']
      obj['height'] = obj['h']
      del obj['w'], obj['h']

    object_ = Object(**obj)

    object_.attributes = attrs
    object_map[oid] = object_

  return object_map, object_

"""
Modified version of `utils.ParseGraph`.

Note
----
- synset data for objects is not provided in the downloadable .json files, so synset
  is not included in the loaded Object, Relationship, and Attribute objects
- currently attributes are a list of strings in Object instances (see `MapObject`)
"""
global count_miss
count_miss = 0
def ParseGraphLocal(data, image):
  global count_hit
  global count_miss

  objects = []
  object_map = {}
  relationships = []
  for obj in data['objects']:
    object_map, o_ = MapObject(object_map, obj)
    objects.append(o_)
  for rel in data['relationships']:
    if rel['subject_id'] in object_map and rel['object_id'] in object_map:
      object_map, s = MapObject(object_map, {'object_id': rel['subject_id']})
      v = rel['predicate']
      object_map, o = MapObject(object_map, {'object_id': rel['object_id']})
      rid = rel['relationship_id']
      relationships.append(Relationship(rid, s, v, o, rel['synsets']))
    else:
      count_miss += 1
    if count_miss % 10000 == 1:
      print 'Misses: ', count_miss
      # print 'SKIPPING   s: {}, v: {}, o: {}'.format(rel['subject_id'], rel['relationship_id'], rel['object_id'])
  return Graph(image, objects, relationships, [])


# Instead of using the following methods yourself, you can download
#   .jsons segmented with these methods from:
#   https://drive.google.com/file/d/0Bygumy5BKFtcQW9yYjhVV0xRSVU/view?usp=sharing



"""
Save a separate .json file for each image id in `imageDataDir`.

Instead of using the following methods yourself, you can download .jsons
  segmented with these methods from:


Notes
-----
- If we don't save .json's by id, `scene_graphs.json` is >6G in RAM.
- Required for `GetSceneGraphs`, which initializes SceneGraph instances
- `imageDataDir` will fill about 1.1G of space on disk
- Run `AddAttrsToSceneGraphs` before `ParseGraphLocal` will work

Each output .json has the following keys:
  - "id"
  - "attributes"
  - "objects"
  - "relationships"
"""
def SaveSceneGraphsById(dataDir='data/', imageDataDir='data/by-id/'):
    if not os.path.exists(imageDataDir): os.mkdir(imageDataDir)
    data = {
            'relationships': ['item.regions.item', 'scene_graphs.json'],
             'objects': ['item', 'objects.json']
     }
    for (graph_attribute, attr_data) in data.iteritems():
        with open('/home/francoisp/Documents/Programmation/benchmark-data/VisualGenome/data/%s' % attr_data[1]) as regions_data:
            current_image_id = 1
            current_image_data = []
            items = ijson.items(regions_data, attr_data[0])
            for item in items:
                if(current_image_id != item['image_id']):
                    img_fname = str(current_image_id) + '.json'
                    image_fpath = os.path.join(imageDataDir, img_fname)
                    if os.path.exists(image_fpath):
                        with open(os.path.join(imageDataDir, img_fname), 'r') as f:
                            graph = json.load(f)
                    else:
                        graph = {}                    
                    with open(os.path.join(imageDataDir, img_fname), 'w') as f:
                        graph[graph_attribute] = current_image_data
                        json.dump(graph, f)
                    current_image_data = []
                    current_image_id = item['image_id']
                values = item[graph_attribute]
                if(len(values) > 0):
                    current_image_data += values
    gc.collect()  # clear memory



"""
Add attributes to scene_graph.json, since these are currently not included.

This also adds a unique id to each attribute, and separates individual
attibutes for each object (these are grouped in attributes.json).

"""
def AddAttrsToSceneGraphs(dataDir='data/'):
  attr_data = json.load(open(os.path.join(dataDir, 'attributes.json')))
  with open(os.path.join(dataDir, 'scene_graphs.json')) as f:
    sg_dict = {sg['image_id']:sg for sg in json.load(f)}

  id_count = 0
  for img_attrs in attr_data:
    attrs = []
    for attribute in img_attrs['attributes']:
      a = img_attrs.copy(); del a['attributes']
      a['attribute']    = attribute
      a['attribute_id'] = id_count
      attrs.append(a)
      id_count += 1
    iid = img_attrs['image_id']
    sg_dict[iid]['attributes'] = attrs

  with open(os.path.join(dataDir, 'scene_graphs.json'), 'w') as f:
    json.dump(sg_dict.values(), f)
  del attr_data, sg_dict
  gc.collect()





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
def GetSceneGraphsVRD(json_file='data/vrd/json/test.json'):
  scene_graphs = []
  with open(json_file,'r') as f:
    D = simplejson.load(f)

  scene_graphs = [ParseGraphVRD(d) for d in D]
  return scene_graphs


def ParseGraphVRD(d):
  image = Image(d['photo_id'], d['filename'], d['width'], d['height'], '', '')

  id2obj = {}
  objs = []
  rels = []
  atrs = []

  for i,o in enumerate(d['objects']):
    b = o['bbox']
    obj = Object(i, b['x'], b['y'], b['w'], b['h'], o['names'], [])
    id2obj[i] = obj
    objs.append(obj)

    for j,a in enumerate(o['attributes']):
      atrs.append(Attribute(j, obj, a['attribute'], []))

  for i,r in enumerate(d['relationships']):
    s = id2obj[r['objects'][0]]
    o = id2obj[r['objects'][1]]
    v = r['relationship']
    rels.append(Relationship(i, s, v, o, []))

  return Graph(image, objs, rels, atrs)


import os
import gc
import json
import visual_genome.utils as utils
from visual_genome.models import (Image, Object, Attribute, Relationship,
                                  Graph, Synset)


def get_all_image_data(data_dir=None):
    """
    Get Image ids from start_index to end_index.
    """
    if data_dir is None:
        data_dir = utils.get_data_dir()
    dataFile = os.path.join(data_dir, 'image_data.json')
    data = json.load(open(dataFile))
    return [utils.parse_image_data(image) for image in data]


def get_all_region_descriptions(data_dir=None):
    """
    Get all region descriptions.
    """
    if data_dir is None:
        data_dir = utils.get_data_dir()
    data_file = os.path.join(data_dir, 'region_descriptions.json')
    image_data = get_all_image_data(data_dir)
    image_map = {}
    for d in image_data:
        image_map[d.id] = d
    images = json.load(open(data_file))
    output = []
    for image in images:
        output.append(utils.parse_region_descriptions(
            image['regions'], image_map[image['id']]))
    return output


def get_all_qas(data_dir=None):
    """
    Get all question answers.
    """
    if data_dir is None:
        data_dir = utils.get_data_dir()
    data_file = os.path.join(data_dir, 'question_answers.json')
    image_data = get_all_image_data(data_dir)
    image_map = {}
    for d in image_data:
        image_map[d.id] = d
    images = json.load(open(data_file))
    output = []
    for image in images:
        output.append(utils.parse_QA(image['qas'], image_map))
    return output


# --------------------------------------------------------------------------------------------------
# get_scene_graphs and sub-methods


def get_scene_graph(image_id, images='data/',
                    image_data_dir='data/by-id/',
                    synset_file='data/synsets.json'):
    """
    Load a single scene graph from a .json file.
    """
    if type(images) is str:
        # Instead of a string, we can pass this dict as the argument `images`
        images = {img.id: img for img in get_all_image_data(images)}

    fname = str(image_id) + '.json'
    image = images[image_id]
    data = json.load(open(image_data_dir + fname, 'r'))

    scene_graph = parse_graph_local(data, image)
    scene_graph = init_synsets(scene_graph, synset_file)
    return scene_graph


def get_scene_graphs(start_index=0, end_index=-1,
                     data_dir='data/', image_data_dir='data/by-id/',
                     min_rels=0, max_rels=100):
    """
    Get scene graphs given locally stored .json files;
    requires `save_scene_graphs_by_id`.

    start_index, end_index : get scene graphs listed by image,
                           from start_index through end_index
    data_dir : directory with `image_data.json` and `synsets.json`
    image_data_dir : directory of scene graph jsons saved by image id
                   (see `save_scene_graphs_by_id`)
    min_rels, max_rels: only get scene graphs with at least / less
                      than this number of relationships
    """
    images = {img.id: img for img in get_all_image_data(data_dir)}
    scene_graphs = []

    img_fnames = os.listdir(image_data_dir)
    if (end_index < 1):
        end_index = len(img_fnames)

    for fname in img_fnames[start_index: end_index]:
        image_id = int(fname.split('.')[0])
        scene_graph = get_scene_graph(
            image_id, images, image_data_dir, data_dir + 'synsets.json')
        n_rels = len(scene_graph.relationships)
        if (min_rels <= n_rels <= max_rels):
            scene_graphs.append(scene_graph)

    return scene_graphs


def map_object(object_map, obj):
    """
    Use object ids as hashes to `visual_genome.models.Object` instances.
    If item not in table, create new `Object`. Used when building
    scene graphs from json.
    """

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


global count_skips
count_skips = [0, 0]


def parse_graph_local(data, image, verbose=False):
    """
    Modified version of `utils.ParseGraph`.
    """
    global count_skips
    objects = []
    object_map = {}
    relationships = []
    attributes = []

    for obj in data['objects']:
        object_map, o_ = map_object(object_map, obj)
        objects.append(o_)
    for rel in data['relationships']:
        if rel['subject_id'] in object_map and rel['object_id'] in object_map:
            object_map, s = map_object(
                object_map, {'object_id': rel['subject_id']})
            v = rel['predicate']
            object_map, o = map_object(
                object_map, {'object_id': rel['object_id']})
            rid = rel['relationship_id']
            relationships.append(Relationship(rid, s, v, o, rel['synsets']))
        else:
            # Skip this relationship if we don't have the subject and object in
            # the object_map for this scene graph. Some data is missing in this
            # way.
            count_skips[0] += 1
    if 'attributes' in data:
        for attr in data['attributes']:
            a = attr['attribute']
            if a['object_id'] in object_map:
                attributes.append(Attribute(attr['attribute_id'],
                                            Object(a['object_id'], a['x'],
                                                   a['y'], a['w'], a['h'],
                                                   a['names'], a['synsets']),
                                            a['attributes'], a['synsets']))
            else:
                count_skips[1] += 1
    if verbose:
        print('Skipped {} rels, {} attrs total'.format(*count_skips))
    return Graph(image, objects, relationships, attributes)


def init_synsets(scene_graph, synset_file):
    """
    Convert synsets in a scene graph from strings to Synset objects.
    """
    syn_data = json.load(open(synset_file, 'r'))
    syn_class = {s['synset_name']: Synset(
        s['synset_name'], s['synset_definition']) for s in syn_data}

    for obj in scene_graph.objects:
        obj.synsets = [syn_class[sn] for sn in obj.synsets]
    for rel in scene_graph.relationships:
        rel.synset = [syn_class[sn] for sn in rel.synset]
    for attr in scene_graph.attributes:
        obj.synset = [syn_class[sn] for sn in attr.synset]

    return scene_graph


# --------------------------------------------------------------------------------------------------
# This is a pre-processing step that only needs to be executed once.
# You can download .jsons segmented with these methods from:
#     https://drive.google.com/file/d/0Bygumy5BKFtcQ1JrcFpyQWdaQWM


def save_scene_graphs_by_id(data_dir='data/', image_data_dir='data/by-id/'):
    """
    Save a separate .json file for each image id in `image_data_dir`.

    Notes
    -----
    - If we don't save .json's by id, `scene_graphs.json` is >6G in RAM
    - Separated .json files are ~1.1G on disk
    - Run `add_attrs_to_scene_graphs` before `parse_graph_local` will work
    - Attributes are only present in objects, and do not have synset info

    Each output .json has the following keys:
      - "id"
      - "objects"
      - "relationships"
    """
    if not os.path.exists(image_data_dir):
        os.mkdir(image_data_dir)

    all_data = json.load(open(os.path.join(data_dir, 'scene_graphs.json')))
    for sg_data in all_data:
        img_fname = str(sg_data['image_id']) + '.json'
        with open(os.path.join(image_data_dir, img_fname), 'w') as f:
            json.dump(sg_data, f)

    del all_data
    gc.collect()  # clear memory


def add_attrs_to_scene_graphs(data_dir='data/'):
    """
    Add attributes to `scene_graph.json`, extracted from `attributes.json`.

    This also adds a unique id to each attribute, and separates individual
    attibutes for each object (these are grouped in `attributes.json`).
    """
    attr_data = json.load(open(os.path.join(data_dir, 'attributes.json')))
    with open(os.path.join(data_dir, 'scene_graphs.json')) as f:
        sg_dict = {sg['image_id']: sg for sg in json.load(f)}

    id_count = 0
    for img_attrs in attr_data:
        attrs = []
        for attribute in img_attrs['attributes']:
            a = img_attrs.copy()
            del a['attributes']
            a['attribute'] = attribute
            a['attribute_id'] = id_count
            attrs.append(a)
            id_count += 1
        iid = img_attrs['image_id']
        sg_dict[iid]['attributes'] = attrs

    with open(os.path.join(data_dir, 'scene_graphs.json'), 'w') as f:
        json.dump(sg_dict.values(), f)
    del attr_data, sg_dict
    gc.collect()


# --------------------------------------------------------------------------------------------------
# For info on VRD dataset, see:
#   http://cs.stanford.edu/people/ranjaykrishna/vrd/

def get_scene_graphs_VRD(json_file='data/vrd/json/test.json'):
    """
    Load VRD dataset into scene graph format.
    """
    scene_graphs = []
    with open(json_file, 'r') as f:
        D = json.load(f)

    scene_graphs = [parse_graph_VRD(d) for d in D]
    return scene_graphs


def parse_graph_VRD(d):
    image = Image(d['photo_id'], d['filename'], d[
                  'width'], d['height'], '', '')

    id2obj = {}
    objs = []
    rels = []
    atrs = []

    for i, o in enumerate(d['objects']):
        b = o['bbox']
        obj = Object(i, b['x'], b['y'], b['w'], b['h'], o['names'], [])
        id2obj[i] = obj
        objs.append(obj)

        for j, a in enumerate(o['attributes']):
            atrs.append(Attribute(j, obj, a['attribute'], []))

    for i, r in enumerate(d['relationships']):
        s = id2obj[r['objects'][0]]
        o = id2obj[r['objects'][1]]
        v = r['relationship']
        rels.append(Relationship(i, s, v, o, []))

    return Graph(image, objs, rels, atrs)

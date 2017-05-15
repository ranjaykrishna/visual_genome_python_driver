
import json
import requests
from os.path import dirname, realpath, join
from visual_genome.models import (Image, Object, Attribute, Relationship,
                                  Region, Graph, QA, QAObject, Synset)


def get_data_dir():
    """
    Get the local directory where the Visual Genome data is locally stored.
    """
    data_dir = join(dirname(realpath('__file__')), 'data')
    return data_dir


def retrieve_data(request):
    """
    Helper Method used to get all data from request string.
    """
    url = 'http://visualgenome.org'
    data = requests.get(url + request).json()
    # connection = httplib.HTTPSConnection("visualgenome.org", '443')
    # connection.request("GET", request)
    # response = connection.getresponse()
    # jsonString = response.read()
    # data = json.loads(json_string)
    return data


def parse_synset(canon):
    """
    Helper to Extract Synset from canon object.
    """
    if len(canon) == 0:
        return None
    return Synset(canon[0]['synset_name'], canon[0]['synset_definition'])


def parse_graph(data, image):
    """
    Helper to parse a Graph object from API data.
    """
    objects = []
    object_map = {}
    relationships = []
    attributes = []
    # Create the Objects
    for obj in data['bounding_boxes']:
        names = []
        synsets = []
        for bbx_obj in obj['boxed_objects']:
            names.append(bbx_obj['name'])
            synsets.append(parse_synset(bbx_obj['object_canon']))
            object_ = Object(obj['id'], obj['x'], obj['y'], obj[
                             'width'], obj['height'], names, synsets)
            object_map[obj['id']] = object_
        objects.append(object_)
    # Create the Relationships
    for rel in data['relationships']:
        relationships.append(Relationship(rel['id'],
                                          object_map[rel['subject']],
                                          rel['predicate'],
                                          object_map[rel['object']],
                                          parse_synset(
                                          rel['relationship_canon'])))
    # Create the Attributes
    for atr in data['attributes']:
        attributes.append(Attribute(atr['id'], object_map[atr['subject']],
                                    atr['attribute'],
                                    parse_synset(atr['attribute_canon'])))
    return Graph(image, objects, relationships, attributes)


def parse_image_data(data):
    """
    Helper to parse the image data for one image.
    """
    img_id = data['id'] if 'id' in data else data['image_id']
    url = data['url']
    width = data['width']
    height = data['height']
    coco_id = data['coco_id']
    flickr_id = data['flickr_id']
    image = Image(img_id, url, width, height, coco_id, flickr_id)
    return image


def parse_region_descriptions(data, image):
    """
    Helper to parse region descriptions.
    """
    regions = []
    if 'region_id' in data[0]:
        region_id_key = 'region_id'
    else:
        region_id_key = 'id'
    for info in data:
        regions.append(Region(info[region_id_key], image, info['phrase'],
                              info['x'], info['y'], info['width'],
                              info['height']))
    return regions


def parse_QA(data, image_map):
    """
    Helper to parse a list of question answers.
    """
    qas = []
    for info in data:
        qos = []
        aos = []
        if 'question_objects' in info:
            for qo in info['question_objects']:
                synset = Synset(qo['synset_name'], qo['synset_definition'])
                qos.append(QAObject(qo['entity_idx_start'], qo[
                           'entity_idx_end'], qo['entity_name'], synset))
        if 'answer_objects' in info:
            for ao in info['answer_objects']:
                synset = Synset(ao['synset_name'], ao['synset_definition'])
                aos.append(QAObject(ao['entity_idx_start'], ao[
                           'entity_idx_end'], ao['entity_name'], synset))
        qas.append(QA(info['qa_id'], image_map[info['image_id']],
                      info['question'], info['answer'], qos, aos))
    return qas

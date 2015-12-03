"""
Visual Genome Python API wrapper, models
"""

"""
Image.
  ID         int
  url        hyperlink string
  width      int
  height     int 
"""
class Image:
  def __init__(self, id, url, width, height, coco_id, flickr_id):
    self.id = id
    self.url = url
    self.width = width
    self.height = height
    self.coco_id = coco_id
    self.flickr_id = flickr_id

  def __str__(self):
    return 'id: %d, coco_id: %d, flickr_id: %d, width: %d, url: %s' \
        % (self.id, self.coco_id, self.flickr_id, self.width, self.url)

"""
Region.
  image 		       int
  phrase           string
  x                int
  y                int
  width            int
  height           int
"""
class Region:
  def __init__(self, image, phrase, x, y, width, height):
    self.image = image
    self.phrase = phrase
    self.x = x
    self.y = y
    self.width = width
    self.height = height

  def __str__ (self):
    return 'x: %s, y: %d, width: %d, height: %d, phrase: %s, image: %d' % \
        (self.x, self.y, self.width, self.height, self.phrase, self.image.id)

"""
Graphs contain objects, relationships and attributes
  image            Image
  bboxes           Object array
  relationships    Relationship array
  attributes       Attribute array
"""
class Graph:
  def __init__(self, image, objects, relationships, attributes):
    self.image = image
    self.objects = objects
    self.relationships = relationships
    self.attributes = attributes

"""
Objects.
  id         int
  x          int
  y          int
  width      int
  height     int
  names      string array
  synsets    Synset array
"""
class Object:
  def __init__(self, id, x, y, width, height, names, synsets):
    self.id = id
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.names = names
    self.synsets = synsets

"""
Relationships. Ex, 'man - jumping over - fire hydrant'.
    subject    int
    predicate  string
    object     int
    rel_canon  Synset
"""
class Relationship:
  def __init__(self, subject, predicate, object, synset):
    self.subject = subject
    self.predicate = predicate
    self.object = object
    self.synset = synset

"""
Attributes. Ex, 'man - old'.
  subject    Object
  attribute  string
  synset     Synset
"""
class Attribute:
  def __init__(self, subject, attribute, synset):
    self.subject = subject
    self.attribute = attribute
    self.synset = synset

"""
Question Answer Pairs.
  ID         int
  image      int
  question   string
  answer     string
  q_objects  QAObject array
  a_objects  QAObject array
"""
class QA:
  def __init__(self, id, image, question, answer, question_objects, answer_objects):
    self.id = id
    self.image = image
    self.question = question
    self.answer = answer
    self.q_objects = question_objects
    self.a_objects = answer_objects

"""
Question Answer Objects are localized in the image and refer to a part 
of the question text or the answer text.
  start_idx          int
  end_idx            int
  name               string
  synset_name        string
  synset_definition  string
"""
class QAObject:
  def __init__(self, start_idx, end_idx, name, synset_name, synset_definition):
    self.start_idx = start_idx
    self.end_idx = end_idx
    self.name = name
    self.synset_name = synset_name
    self.synset_definition = synset_definition

"""
Wordnet Synsets.
  name       string
  definition string
"""
class Synset:
  def __init__(self, name, definition):
    self.name = name
    self.definition = definition


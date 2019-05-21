"""
Visual Genome Python API wrapper, models
"""


class Image:
    """
    Image.
      ID         int
      url        hyperlink string
      width      int
      height     int
    """

    def __init__(self, id, url, width, height, coco_id, flickr_id):
        self.id = id
        self.url = url
        self.width = width
        self.height = height
        self.coco_id = coco_id
        self.flickr_id = flickr_id

    def __str__(self):
        return 'id: %d, coco_id: %d, flickr_id: %d, width: %d, url: %s' \
            % (self.id, -1
                if self.coco_id is None
                else self.coco_id, -1
                if self.flickr_id is None
                else self.flickr_id, self.width, self.url)

    def __repr__(self):
        return str(self)


class Region:
    """
    Region.
      image 		   int
      phrase           string
      x                int
      y                int
      width            int
      height           int
    """

    def __init__(self, id, image, phrase, x, y, width, height):
        self.id = id
        self.image = image
        self.phrase = phrase
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        stat_str = 'id: {0}, x: {1}, y: {2}, width: {3},' \
                   'height: {4}, phrase: {5}, image: {6}'
        return stat_str.format(self.id, self.x, self.y,
                               self.width, self.height, self.phrase,
                               self.image.id)

    def __repr__(self):
        return str(self)


class Graph:
    """
    Graphs contain objects, relationships and attributes
      image            Image
      bboxes           Object array
      relationships    Relationship array
      attributes       Attribute array
    """

    def __init__(self, image, objects, relationships, attributes):
        self.image = image
        self.objects = objects
        self.relationships = relationships
        self.attributes = attributes


class Object:
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

    def __init__(self, id, x, y, width, height, names, synsets):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.names = names
        self.synsets = synsets

    def __str__(self):
        name = self.names[0] if len(self.names) != 0 else 'None'
        return '%s' % (name)

    def __repr__(self):
        return str(self)


class Relationship:
    """
    Relationships. Ex, 'man - jumping over - fire hydrant'.
        subject    int
        predicate  string
        object     int
        phrase     string
        rel_canon  Synset
        image      int
    """

    def __init__(self, id, image, subject, predicate, object, synsets):
        self.id = id
        self.image = image
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.synsets = synsets
        if self.object.get('names')!=None:
            object1=''.join(self.object.get('names'))
        else:
            object1=self.object.get('name')
        if self.subject.get('names')!=None:
            subject=''.join(self.subject.get('names'))
        else:
            subject=self.subject.get('name')
        #predicate=self.predicate
        self.phrase=subject+' '+self.predicate.lower()+' '+object1     
  
        

    def __str__(self):        
        stat_str = 'id: {0}, subject: {1}, object: {2}, predicate: {3},' \
                   ' phrase: {4}, image: {5}'
        return stat_str.format(self.id, self.subject,self.predicate, self.object,self.phrase,self.image.id)


    def __repr__(self):
        return str(self)


class Attribute:
    """
    Attributes. Ex, 'man - old'.
      subject    Object
      attribute  string
      synset     Synset
    """

    def __init__(self, id, image,subject,w,h,x,y, attribute, synset):
        self.id = id
        self.image=image
        self.subject = ''.join(subject)
        self.attribute = ', '.join(attribute)
        self.synset = synset

    def __str__(self):
        return "%d: %s is %s" % (self.id, self.subject, self.attribute)

    def __repr__(self):
        return str(self)


class QA:
    """
    Question Answer Pairs.
      ID         int
      image      int
      question   string
      answer     string
      q_objects  QAObject array
      a_objects  QAObject array
    """

    def __init__(self, id, image, question, answer,
                 question_objects, answer_objects):
        self.id = id
        self.image = image
        self.question = question
        self.answer = answer
        self.q_objects = question_objects
        self.a_objects = answer_objects

    def __str__(self):
        return 'id: %d, image: %d, question: %s, answer: %s' \
            % (self.id, self.image.id, self.question, self.answer)

    def __repr__(self):
        return str(self)


class QAObject:
    """
    Question Answer Objects are localized in the image and refer to a part
    of the question text or the answer text.
      start_idx          int
      end_idx            int
      name               string
      synset_name        string
      synset_definition  string
    """

    def __init__(self, start_idx, end_idx, name, synset):
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.name = name
        self.synset = synset

    def __repr__(self):
        return str(self)


class Synset:
    """
    Wordnet Synsets.
      name       string
      definition string
    """

    def __init__(self, name, definition):
        self.name = name
        self.definition = definition

    def __str__(self):
        return '{} - {}'.format(self.name, self.definition)

    def __repr__(self):
        return str(self)

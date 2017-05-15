
import visual_genome.utils as utils


def get_all_image_ids():
    """
    Get all Image ids.
    """
    page = 1
    next = '/api/v0/images/all?page=' + str(page)
    ids = []
    while True:
        data = utils.retrieve_data(next)
        ids.extend(data['results'])
        if data['next'] is None:
            break
        page += 1
        next = '/api/v0/images/all?page=' + str(page)
    return ids


def get_image_ids_in_range(start_index=0, end_index=99):
    """
    Get Image ids from start_index to end_index.
    """
    ids_per_page = 1000
    start_page = start_index / ids_per_page + 1
    endPage = end_index / ids_per_page + 1
    ids = []
    for page in range(start_page, endPage + 1):
        data = utils.retrieve_data('/api/v0/images/all?page=' + str(page))
        ids.extend(data['results'])
    ids = ids[start_index % 100:]
    ids = ids[:end_index - start_index + 1]
    return ids


def get_image_data(id=61512):
    """
    Get data about an image.
    """
    data = utils.retrieve_data('/api/v0/images/' + str(id))
    if 'detail' in data and data['detail'] == 'Not found.':
        return None
    image = utils.parse_image_data(data)
    return image


def get_region_descriptions_of_image(id=61512):
    """
    Get the region descriptions of an image.
    """
    image = get_image_data(id=id)
    data = utils.retrieve_data('/api/v0/images/' + str(id) + '/regions')
    if 'detail' in data and data['detail'] == 'Not found.':
        return None
    return utils.parse_region_descriptions(data, image)


def get_region_graph_of_region(image_id=61512, region_id=1):
    """
    Get Region Graph of a particular Region in an image.
    """
    image = get_image_data(id=image_id)
    data = utils.retrieve_data(
        '/api/v0/images/' + str(image_id) + '/regions/' + str(region_id))
    if 'detail' in data and data['detail'] == 'Not found.':
        return None
    return utils.parse_graph(data[0], image)


def get_scene_graph_of_image(id=61512):
    """
    Get Scene Graph of an image.
    """
    image = get_image_data(id=id)
    data = utils.retrieve_data('/api/v0/images/' + str(id) + '/graph')
    if 'detail' in data and data['detail'] == 'Not found.':
        return None
    return utils.parse_graph(data, image)


def get_all_QAs(qtotal=100):
    """
    Gets all the QA from the dataset.
    qtotal: int       total number of QAs to return.
                      Set to None if all QAs should be returned
    """
    page = 1
    next = '/api/v0/qa/all?page=' + str(page)
    qas = []
    image_map = {}
    while True:
        data = utils.retrieve_data(next)
        for d in data['results']:
            if d['image'] not in image_map:
                image_map[d['image']] = get_image_data(id=d['image'])
        qas.extend(utils.parse_QA(data['results'], image_map))
        if qtotal is not None and len(qas) > qtotal:
            return qas
        if data['next'] is None:
            break
        page += 1
        next = '/api/v0/qa/all?page=' + str(page)
    return qas


def get_QA_of_type(qtype='why', qtotal=100):
    """
    Get all QA's of a particular type - example, 'why'
    qtype: string    possible values: what, where, when, why, who, how.
    qtotal: int      total number of QAs to return.
                     Set to None if all QAs should be returned
    """
    page = 1
    next = '/api/v0/qa/' + qtype + '?page=' + str(page)
    qas = []
    image_map = {}
    while True:
        data = utils.retrieve_data(next)
        for d in data['results']:
            if d['image'] not in image_map:
                image_map[d['image']] = get_image_data(id=d['image'])
        qas.extend(utils.parse_QA(data['results'], image_map))
        if qtotal is not None and len(qas) > qtotal:
            return qas
        if data['next'] is None:
            break
        page += 1
        next = '/api/v0/qa/' + qtype + '?page=' + str(page)
    return qas


def get_QA_of_image(id=61512):
    """
    Get all QAs for a particular image.
    """
    page = 1
    next = '/api/v0/image/' + str(id) + '/qa?page=' + str(page)
    qas = []
    image_map = {}
    while True:
        data = utils.retrieve_data(next)
        for d in data['results']:
            if d['image'] not in image_map:
                image_map[d['image']] = get_image_data(id=d['image'])
        qas.extend(utils.parse_QA(data['results'], image_map))
        if data['next'] is None:
            break
        page += 1
        next = '/api/v0/image/' + str(id) + '/qa?page=' + str(page)
    return qas

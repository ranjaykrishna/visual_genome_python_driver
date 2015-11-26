# Visual Genome Python Driver
A python wrapper for the Visual Genome API

To send a request to the server, call requestHandler in module handle_request.

Default argument values:
	requestHandler(request_type="", image_id=0, qa_type="", image_options="", take_all=False)

Arguement value space:
	request_type: {"images", "image", "qa"}
  image_id: int
  (optional)qa_type: {"what", "when", "who", "why", "which", "where", "how"}
  (optional)image_options: {"regions", "graph"}
  take_all: boolean
    
Mapping between argument values and http requests:
  GET images/all
    request_type="images", take_all=True
  GET images/:id
    request_type="images", image_id=:id
	GET images/:id/regions
    request_type="images", image_id=:id, image_options="regions"
 	GET images/:id/graph
    request_type="images", image_id=:id, image_options="graph"
  GET image/:id/qa
    request_type="image", image_id=:id
  GET qa/all
    request_type="qa", take_all=True
  GET qa/:q7w_type
    request_type="qa", qa_type=q7w_type
    
Python objects returned by specific requests:
  GET images/all
    Result value: an ImageData object
        
  GET images/:id
    Result value: an Image object
        
  GET images/:id/regions
    Result value: a Region array
        
  GET images/:id/graph
    Result value: a Graph object
        
  GET image/:id/qa
    Result value: a QA array
        
  GET qa/all
    Result value: a QA array
        
  GET qa/:q7w_type
    Result value: a QA array
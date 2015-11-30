# Visual Genome Python Driver
A python wrapper for the Visual Genome API

The complete list of object models is in https://visualgenome.org/api/v0/api_object_model.html

The list of supported http requests is in https://visualgenome.org/api/v0/api_endpoint_reference.html

To send a request to the server using this wrapper, call requestHandler in module handle_request.

Default argument values:  
requestHandler(request_type="", image_id=0, qa_type="", image_options="",take_all=False)

Arguement value space:  
request_type: {"images", "image", "qa"}  
image_id: int  
(optional)qa_type: {"what", "when", "who", "why", "which", "where", "how"}  
(optional)image_options: {"regions", "graph"}  
take_all: boolean
    
Mapping between argument values and http requests:  
GET images/all  
request_type="images", take_all=True  
Returns an ImageData object

GET images/:id  
request_type="images", image_id=:id  
Returns an Image object

GET images/:id/regions  
request_type="images", image_id=:id, image_options="regions"  
Returns a Region array

GET images/:id/graph  
request_type="images", image_id=:id, image_options="graph"  
Returns a Graph object

GET image/:id/qa  
request_type="image", image_id=:id  
Returns a QA array

GET qa/all  
request_type="qa", take_all=True  
Returns a QA array

GET qa/:q7w_type  
request_type="qa", qa_type=q7w_type  
Returns a QA array
    

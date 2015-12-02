# Visual Genome Python Driver
A python wrapper for the [Visual Genome API](http://visualgenome.org/api/v0/). Visit the website for a complete list of [object models](http://visualgenome.org/api/v0/api_object_model.html) and details about all [endpoints](http://visualgenome.org/api/v0/api_endpoint_reference.html). Look at our demo to see how you can use the python driver to access all the Visual Genome data.

### Python Wrapper

#### Get all Visual Genome image ids
All the data in Visual Genome must be accessed per image. Each image is identified by a unique id. So, the first step is to get the list of all image ids in the Visual Genome dataset.

````python
> from src import controllers
> ids = controllers.GetAllImageIds()
> print ids[0]
1
````

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

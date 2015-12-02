# Visual Genome Python Driver
A python wrapper for the [Visual Genome API](http://visualgenome.org/api/v0/). Visit the website for a complete list of [object models](http://visualgenome.org/api/v0/api_object_model.html) and details about all [endpoints](http://visualgenome.org/api/v0/api_endpoint_reference.html). Look at our demo to see how you can use the python driver to access all the Visual Genome data.

#### Get all Visual Genome image ids
All the data in Visual Genome must be accessed per image. Each image is identified by a unique id. So, the first step is to get the list of all image ids in the Visual Genome dataset.

````python
> from src import vg
> ids = vg.GetAllImageIds()
> print ids[0]
1
````

`ids` is a python array of integers where each integer is an image id.

#### Get a range of Visual Genome image ids
There are 108,249 images currently in the Visual Genome dataset. Instead of getting all the image ids, you might want to just get the ids of a few images. To get the ids of images 2000 to 2010, you can use the following code:

````python
> ids = vg.GetImageIdsInRange(startIndex=2000, endIndex=2010)
> print ids
[2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011]
````

#### Get image data

#### Get Region Descriptions for an image

#### Get Scene Graph for an image

#### Get Question Answers for an image

#### Get all Questions Answers in the dataset

#### Get one type of Questions Answers from  the entire dataset

### License
MIT License copyright Ranjay Krishna

### Questions? Comments?
My hope is that the API and the python wrapper are so easy that you never have to ask questions. But if you have any question, you can contact me directly at ranjaykrishna at gmail or contact the project at stanfordvisualgenome @ gmail.

Follow us on Twitter:
- [@RanjayKrishna](https://twitter.com/RanjayKrishna)
- [@VisualGenome](https://twitter.com/visualgenome)

### Want to Help?
If you'd like to help, write example code, contribute patches, document things on the wiki, tweet about it. Your help is always appreciated!


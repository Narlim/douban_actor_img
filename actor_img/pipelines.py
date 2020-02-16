from scrapy.pipelines.images import ImagesPipeline
import hashlib
from scrapy.utils.python import to_bytes
import time

class ActorImgPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        times = time.strftime("%Y-%m-%d-%H", time.localtime()) 
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return '%s/%s.jpg' % (times, image_guid)

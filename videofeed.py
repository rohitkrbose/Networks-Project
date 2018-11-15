import cv2
import numpy
import io
from PIL import Image

class VideoFeed:

    def __init__(self,mode=1,name="w1",capture=1):
        print name
        self.camera_index = 0
        self.name = name
        if capture == 1:
            self.cam = cv2.VideoCapture(self.camera_index)

    def get_frame(self):
        ret_val, img = self.cam.read()
        if (ret_val == False):
             print ('None image get frame')
        c = cv2.waitKey(1)
        cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im)
        b = io.BytesIO()
        pil_im.save(b, 'jpeg')
        im_bytes = b.getvalue()
        return im_bytes

    def set_frame(self, frame_bytes):
        pil_bytes = io.BytesIO(frame_bytes)
        # if (frame_bytes == None):
        #     print ('Set frame none')
        pil_image = Image.open(pil_bytes)
        # cv_image = numpy.asarray(pil_image.convert('RGB'))
        cv_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        # cv2.imshow(self.name, cv_image)
        return (cv_image)

if __name__=="__main__":
    vf = VideoFeed(1,"test",1)
    while 1:
        m = vf.get_frame()
        vf.set_frame(m)


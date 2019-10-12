# Refer to this link for  getting started https://pypi.org/project/google-cloud-vision/
# Also please make sure you are running python 3.6 or 3.7  or higher
# After installing google cloud vision DO NOT commit the py files for it. If you are using
# Pycharm there should be a Base foulder. Do not commit this. You can add it to the ignore list

# To install google cloud vision please follow instruction on link above

# Google Cloud Vision API Libraries
from google.cloud import vision
from google.oauth2 import service_account

# Command line Argument Parser
import argparse

import os
import io


class ImageAnalyzer(object):
    credentials = service_account.Credentials.from_service_account_file(
        'Brandsense-d2d2f258490c.json')

    def __init__(self, img):
        """
        This will use an object oriented implementation
        All that is needed is the img.
        We also want to upload the image. And prep it for color processing
        :param img:
        :return:
        """

        self.img_path = os.path.abspath(img)

        # Create Client. Use Google's authenticator to set credentials
        # We can also set credentials with
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Brandsense-d2d2f258490c.json"
        self.client = vision.ImageAnnotatorClient(credentials=self.credentials)

        with io.open(self.img_path, 'rb') as image_file:
            content = image_file.read()

        # load image for vision use
        self.img = vision.types.Image(content=content)

    def analyze_img(self):
        """
        This acts as a test function. Doesnt output logo just some key words.
        :return:
        """
        response = self.client.label_detection(image=self.img)
        labels = response.label_annotations

        print('Labels:')
        for label in labels:
            print(label.description)

    def get_logo(self):
        """
        From image this prints the logo in the image
        :return:
        list of strings that are the logos that received a .75 score or better
        """
        response = self.client.logo_detection(image=self.img)
        logos = response.logo_annotations

        logos_found = []
        for logo in logos:
            if float(logo.score) > .75:
                logos_found.append(logo.description)
        return logos_found

    def get_color(self):
        """
        We could totally just use google cloud vision for this
        :return:
        """
        pass

    def get_text(self):
        """
        Google cloud vision
        :return:
        """
        pass


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Google Cloud vision implementation for BrandSense')
    # parser.add_argument("--img")

    # args = parser.parse_args()

    # As of now im thinking saving the image to the server would be easiest. It might be cool
    # To add a PostgreSQL thing here where the javascript saves the image to the database.
    # Or we could save it to the database here and just pass a temp location.
    # We could also try using google's Buckets but this might be over complicating things, as then we would
    # be using different databases
    #img_path = args.img
    img_path = "nike-logo.png"
    # Load img to our object
    image_analyzer = ImageAnalyzer(img_path)
    print(image_analyzer.get_logo())


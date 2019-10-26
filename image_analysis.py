# Refer to this link for  getting started https://pypi.org/project/google-cloud-vision/
# Also please make sure you are running python 3.6 or 3.7  or higher
# After installing google cloud vision DO NOT commit the py files for it. If you are using
# Pycharm there should be a Base foulder. Do not commit this. You can add it to the ignore list

# To install google cloud vision please follow instruction on link above

# Google Cloud Vision API Libraries
from google.cloud import vision
from google.oauth2 import service_account

import webcolors

# Command line Argument Parser
import argparse

import psycopg2

import os
import io


class LogoDataBase(object):
    connection = None

    def __init__(self, database, user='postgres', passwd='123', host='localhost', port='5432'):
        """
        Create instance of connection. Saves the connection string if we need to reconnect for any reason.
        :param database: required
        :param user:
        :param passwd:
        :param host:
        :param port:
        """
        try:
            # Create connection string
            self.connection_str = f'user={user} password={passwd} host={host} port={port} dbname={database}'

            self.connect()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def connect(self):
        self.connection = psycopg2.connect(self.connection_str)

    def get_relevant_rows_from_logo(self, logo, logo_color, logo_text):
        """
        get image info. uses tag to create query
        Here is what the library wiki says: Warning Never, never, NEVER use Python string concatenation (+) or string
        parameters interpolation (%) to pass variables to a SQL query string. Not even at gunpoint.
        Here is an example of the correct usage.
        SQL = "INSERT INTO authors (name) VALUES (%s);" # Note: no quotes
        data = ("O'Reilly", )
        cur.execute(SQL, data) # Note: no % operator
        :return:
        """
        # TODO: put this all in a try-catch loop. We need to figure out what exceptions to catch
        if not self.connection:
            return None
        query = "SELECT * FROM logos WHERE logo = %s"
        cursor = self.connection.cursor()

        cursor.execute(query, (logo,))

        matching_logos = []

        row = cursor.fetchone()
        while row:
            # parse row. These commented out line could be useful
            # customer = row[0]
            colors = row[2]
            text = row[3]
            # link = row[4]
            # info = row[5]
            # img = row[6]

            # TODO: the more i think about this, it doesnt work. If we a blue nike logo uploaded it could also output
            #  a pink one if they had the same text. SO we might want to look for both and if we cant find both then
            #  return a single one.
            if len(colors) is 0 and len(text) is 0:
                matching_logos.append(row)
            elif len(set(logo_color).intersection(set(colors))) > 0:
                matching_logos.append(row)
            elif len(set(logo_text).intersection(set(text))) > 0:
                matching_logos.append(row)

            row = cursor.fetchone()
        return matching_logos

    def insert_logo(self, customer, logo, colors, text, link, info):
        # TODO: we need to make this a bit better protected. or we really don't i guess
        cursor = self.connection.cursor()

        logo_insert_query = """INSERT INTO logos(customer , logo, colors, text, link, info)
                                           VALUES(%s, %s, %s, %s, %s, %s);"""
        logo_info = (customer, logo, colors, text, link, info)

        try:
            cursor.execute(logo_insert_query, logo_info)
            self.connection.commit()

            count = cursor.rowcount
            print(count, "Record inserted successfully into mobile table")
            return True
        except:  # TODO make this better, and not a bare exception clause.
            return False


class ImageAnalyzer(object):
    credentials = service_account.Credentials.from_service_account_file(
        'Brandsense-ian.json')

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
        # We can also set credentials with the bellow line. But id rather not
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

    @staticmethod
    def closest_color(r_color):
        """
        Given a color tuple (r, g, b) it outputs the closest color
        :param r_color:
        :return:
        """
        min_colors = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - r_color[0]) ** 2
            gd = (g_c - r_color[1]) ** 2
            bd = (b_c - r_color[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    def get_color(self):
        """
        We could totally just use google cloud vision for this
        :return:
        """
        response = self.client.image_properties(image=self.img)
        props = response.image_properties_annotation
        colors_found = []

        # Only want to top 4 colors
        for color in props.dominant_colors.colors[0:4]:
            requested_color = (int(color.color.red), int(color.color.green), int(color.color.blue))
            try:
                closest_name = webcolors.rgb_to_name(requested_color)
            except ValueError:
                closest_name = self.closest_color(requested_color)
            colors_found.append(closest_name)
        return colors_found

    def get_text(self):
        """
        Google cloud vision, gets text in image
        :return:
        """
        response = self.client.text_detection(image=self.img)
        texts = response.text_annotations

        texts_found = []

        for text in texts:
            # Removes new lines characters
            texts_found.append(text.description.strip('\n'))
        # Google cloud vision likes to include duplicates so this removed them
        return list(set(texts_found))


# TODO: these two functions act as examples. We need to figure out how to structure them
def user_execution(img_loc):
    """
    This may be en example of a function the user would call.
    The user would click on the button and it would provide the result from the db
    :param img_loc: location in server file system
    :return: array of strings to be displayed
    """
    # we will create a new instance of the database connection.
    db = LogoDataBase(database="brandsense_db")
    # Create instance of our image analysis. This will create our cloud vision image obj
    image_analyzer = ImageAnalyzer(img_loc)

    logos = image_analyzer.get_logo()
    if len(logos) is not 0:
        text = image_analyzer.get_text()
        colors = image_analyzer.get_color()

        # An image could have multiple logos. For now we will search for all of them
        relevant_rows = []
        for logo in logos:
            relevant_rows.append(db.get_relevant_rows_from_logo(logo, colors, text))
        # This should always be in the form of a multidimensional array of strings

        if len(relevant_rows[0]) is 0:
            return logos
        return relevant_rows

    else:
        # Not totally sure what we want to do here
        return "Could not find Logo"


def client_upload(customer, link, info, img_loc):
    """
    With provided link and img. we will upload to database. This is a big work in progress.
    Im not sure what we want here.
    :param customer:
    :param link:
    :param info:
    :param img_loc:
    :return:
    """
    # TODO: Add duplicate upload prevention.
    # we will create a new instance of the database connection.
    db = LogoDataBase(database="brandsense_db")
    # Create instance of our image analysis. This will create our cloud vision image obj
    image_analyzer = ImageAnalyzer(img_loc)

    logos = image_analyzer.get_logo()
    if len(logos) is not 0:
        text = image_analyzer.get_text()
        colors = image_analyzer.get_color()
        for logo in logos:
            # This might be a special case for more than one logo. right now we only want the first
            if not db.insert_logo(customer, logo, colors, text, link, info):
                return "failed upload"
            break
        return "Successful upload"
    else:
        return "Failed to add image"


if __name__ == '__main__':
    # To use this file, run as such: image_analysis.py --img=nike-logo.png
    parser = argparse.ArgumentParser(description='Google Cloud vision implementation for BrandSense')
    parser.add_argument("--img")
    parser.add_argument("--user")

    # simple argument parser. to get image from running command, and user.
    args = parser.parse_args()
    img_path = args.img

    # 'user' or 'client'.
    if args.user:
        user = args.user
    else:
        user = 'user'

    if img_path:
        print(user)
        if str(user).strip() in 'client':
            print(client_upload('Adidas', 'https://www.adidas.com/us', 'boost product', img_path))
        else:
            print(user_execution(img_path))


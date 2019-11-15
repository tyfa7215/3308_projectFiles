# Refer to this link for  getting started https://pypi.org/project/google-cloud-vision/
# Also please make sure you are running python 3.6 or 3.7  or higher
# After installing google cloud vision DO NOT commit the py files for it. If you are using
# Pycharm there should be a Base folder. Do not commit this. You can add it to the ignore list

# To install google cloud vision please follow instruction on link above

# Google Cloud Vision API Libraries
from google.cloud import vision
from google.oauth2 import service_account

import webcolors

import psycopg2

import os
import io
import sys
import string

# This was added to clean the text. We don't want as much jiberish.
stop_words = ['tm', 'all', 'just', 'brands', 'being', 'over', 'both', 'through', 'may', 'copyright', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once']


class LogoDataBase(object):
    connection = None

    def __init__(self, database='brandsense_db', user='postgres', passwd='123', host='localhost', port='5432'):
        """
        Create instance of connection. Saves the connection string if we need to reconnect for any reason.
        :param database: required
        :param user:
        :param passwd:
        :param host:
        :param port:
        """
        try:
            # Create connection string. This lib does also have another ctor for this but this wat we can easily
            # save our creds.
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

        try:
            cursor.execute(query, (logo,))
        except(Exception, psycopg2.Error):
            print("Failed to execute postgres query")
            return []

        matching_logos = []

        row = cursor.fetchone()
        while row:
            # parse row. These commented out line could be useful
            logo_id = row[0]
            colors = row[3]
            text = row[4]
            # link = row[4]
            # info = row[5]
            # img = row[6]

            # TODO: the more i think about this, it doesnt work. If a blue nike logo uploaded it could also output
            #  a pink one if they had the same text. SO we might want to look for both and if we cant find both then
            #  return a single one. But we could also just make text specific and this will be ok.
            if len(colors) is 0 and len(text) is 0:
                matching_logos.append(logo_id)
            elif len(set(logo_color).intersection(set(colors))) > 0:
                matching_logos.append(logo_id)
            elif len(set(logo_text).intersection(set(text))) > 0:
                matching_logos.append(logo_id)

            row = cursor.fetchone()
        return matching_logos

    def insert_logo(self, customer, logo, colors, text, link, info):
        # TODO: we need to make this a bit better protected. or we really don't i guess
        cursor = self.connection.cursor()

        logo_insert_query = """INSERT INTO logos(customer ,logo , colors, text, link, info)
                                           VALUES(%s, %s, %s, %s, %s, %s);"""
        logo_info = (customer, logo, colors, text, link, info)

        try:
            cursor.execute(logo_insert_query, logo_info)
            self.connection.commit()

            count = cursor.rowcount
            print(count, "Record inserted successfully into mobile table")
            return True
        except(Exception, psycopg2.Error):  # as error:
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
            if float(logo.score) > .6:
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
            for text in texts:
                # Removes new lines characters
                w = text.description.strip('\n')
                if w.translate(str.maketrans('', '', string.punctuation)).lower() not in stop_words:
                    texts_found.append(w)
        # Google cloud vision likes to include duplicates so this removed them
        return list(set(texts_found))


def user_execution_db(img_loc):
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
    try:
        logos = image_analyzer.get_logo()
    except Exception as e:
        print("Failed connect. Try again later")
        return "Error"

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
        return f"Error: Unable to detect logo in image"


def user_execution(img_loc):
    """
    This may be en example of a function the user would call.
    The user would click on the button and it would provide the result
    :param img_loc: location in server file system
    :return: array of strings to be displayed
    """
    # Create instance of our image analysis. This will create our cloud vision image obj
    image_analyzer = ImageAnalyzer(img_loc)
    try:
        logos = image_analyzer.get_logo()
    except Exception as e:
        return "Error: failed to establish connection with google cloud vision api. Try again later."

    if len(logos) is not 0:
        text = image_analyzer.get_text()
        colors = image_analyzer.get_color()

        # An image could have multiple logos. For now we will search for all of them
        relevant_rows = []
        for logo in logos:
            relevant_rows.append((logo, text, colors))

        return relevant_rows

    else:
        # Not totally sure what we want to do here
        text = image_analyzer.get_text()
        return "Error: unable to detect logo in image."


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
    # Example Usage: Be careful with the arguments and make sure you use "" around them, as this program assumes the
    # order that the argument are provided.
    # Retrieve analysis from google: image_analysis.py <relative_image_path>
    # Retrieve "relevant rows" from db: image_analysis.py <relative_image_path> T
    # Save data to db: image_analysis.py <relative_image_path> T T <link> <description> <client(optional)>
    # Example image_analysis.py starbucks.jpg T
    img_path = None
    use_db = False
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        if len(sys.argv) > 2:
            use_db = (sys.argv[2].lower() in 't' or sys.argv[2].lower in 'true')
            # We are forced to add these checks because we don't want any extra characters to break this and break the
            # db

    if img_path is None:
        print(f'Image error. Invalid image location: {img_path}')

    if img_path:
        if use_db:
            if len(sys.argv) > 5 and (sys.argv[3].lower() in 't' or sys.argv[3].lower in 'true'):
                # When typing these in, pleas insure you include "" around them
                link_str = sys.argv[4]
                desc_str = sys.argv[5]
                if len(sys.argv) > 6:
                    client_str = sys.argv[6]
                else:
                    client_str = ''
                print(client_upload(client_str, link_str, desc_str, img_path))
            else:
                print(user_execution_db(img_path))
        else:
            print(user_execution(img_path))



# face verification with the VGGFace2 model
import imutils as imutils
from matplotlib import pyplot
from PIL import Image
from numpy import asarray
from scipy.spatial.distance import cosine
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import cv2
import pickle
import time


# extract a single face from a given photograph
def extract_face_for_one(filename, required_size=(224, 224)):
    # load image from file
    pixels = pyplot.imread(filename)
    # create the detector, using default weights
    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    x1, y1, width, height = results[0]['box']
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = asarray(image)
    return face_array


# extract faces for class picture
def extract_faces_for_class(filename, required_size=(224, 224), student=False):

    pixels = cv2.imread(filename)
    # perform face detection
    bboxes = classifier.detectMultiScale(pixels, 1.1, 5)
    faces = []
    # print bounding box for each detected face
    for i, box in enumerate(bboxes):
        x, y, width, height = box
        x2, y2 = x + width, y + height
        face = pixels[y:y2, x:x2]
        face = Image.fromarray(face)
        b, g, r = face.split()
        face = Image.merge("RGB", (r, g, b))

        face = face.resize(required_size)
        face_array = asarray(face)
        # cv2.imshow('im', face_array)
        faces.append(face_array)
        if student and len(faces) > 1:
            return -1
    return faces


# this is what we need to use on every student in order to get embedding
# extract faces and calculate face embeddings for a list of photo files
def get_embeddings(filenames, student=False):
    # extract faces
    if isinstance(filenames, list):
        faces = [extract_face_for_one(f) for f in filenames]
    else:
        faces = extract_faces_for_class(filenames, student=student)
        if faces == -1:
            faces = [extract_face_for_one(filenames)]

    # convert into an array of samples
    samples = asarray(faces, 'float32')
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # perform prediction
    yhat = model.predict(samples)
    return yhat


# determine if a candidate face is a match for a known face
def is_match(known_embedding, candidate_embedding, thresh=0.5):
    # calculate distance between embeddings
    score = cosine(known_embedding, candidate_embedding)
    if score <= thresh:
        return True
    else:
        return False


def is_face_in_class(face, class_embeddings,):
    for i, class_face in enumerate(class_embeddings):
        if is_match(class_face, face):
            return i
    return -1


def find_known_faces(class_embeddings, class_names, filename):
    face_recognition_init()
    known = []
    faces = extract_faces_for_class(filename)
    if not faces:
        return None
    samples = asarray(faces, 'float32')
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # perform prediction
    print('Starting')
    embeddings = model.predict(samples)
    for i, face in enumerate(embeddings):
        result = is_face_in_class(face, class_embeddings)
        if result != -1:
            known.append(class_names[result])
    return known


# getting an image link and saving embedding in wanted link
def save_embedding(image_link, embedding_link):
    embedding = get_embeddings(image_link, student=True)
    file = open(embedding_link, 'wb')
    pickle.dump(embedding, file)
    file.close()


# required
def face_recognition_init():
    global detector
    global classifier
    global model

    if detector == '':
        detector = MTCNN()
        classifier = cv2.CascadeClassifier('/Users/eitan/mysite/main/haarcascade_frontalface_default.xml')
        model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')


detector = ''
classifier = ''
model = ''


if __name__ == '__main__':
    class_pics = ['yoel1.jpg', 'p3.jpg']
    class_names = ['Yoel', 'Eitan']
    class_embeddings = get_embeddings(class_pics)

    print(class_embeddings[0])

    camera = cv2.VideoCapture(0)
    while True:
        # getting the frame
        grabbed, frame = camera.read()
        frame = imutils.resize(frame, width=700)
        frame = cv2.flip(frame, 1)
        clone = frame.copy()
        Image.fromarray(frame).save('current.jpg')
        print(get_embeddings('current.jpg'))
        cv2.imshow("Video Feed", clone)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


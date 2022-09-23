from ast import main
from webbrowser import get
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import requests
import os

'''GLOBAL VARIABLES'''
# Custom Vision Properties to Set - enter here
ENDPOINT = "xxx"
training_key = "xxx"
# prediction_key = "xxx"
prediction_resource_id = "xxx"
project_id = "xxx"
# Create Trainer Client
credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})

def get_trainer():
    return CustomVisionTrainingClient(ENDPOINT, credentials)

def get_tags(trainer):
    # Total number of images in project (workspace iteration)
    total_count_of_images = trainer.get_image_count(project_id)
    print("Total Count of Images: " + str(total_count_of_images))

    # Get tags in project (workspace iteration)
    raw_tags = trainer.get_tags(project_id)
    tags = []
    for i in raw_tags:
        tags.append(i.name)
    tags.sort()
    return tags

# Download tagged images from Custom Vision (workplace iteration) with chosen tag listed above
# This will create a new directory with the name of the tag and download all images with that tag from the custom vision workspace
# start the download process by setting count of how many images you want to skip
def download_images(count, restart_download, chosen_tag, trainer):
    current_directory = os.getcwd()
    skip_pics = count # set recursively to go through till it get the correct image per tag
    # download images with chosen tag
    tagged_images = trainer.get_tagged_images(
        project_id, tag_ids=[chosen_tag], take=256, skip=skip_pics)

    # for each image, check to see if the tag is the chosen tag
    # if yes then download if not then count until we get to 256 and restart the process
    for i in tagged_images:
        print("Image Count: " + str(count))
        count += 1
        if (i.tags[0].tag_name == chosen_tag):
            print('Downloading image ' + i.id + '...')
            url = i.original_image_uri
            response = requests.get(url)
            filepath = os.path.join(
                current_directory, "{}/{}.jpg".format(chosen_tag, i.id))
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
            open(filepath, "wb").write(response.content)
        else:
            print('Image not Found: Tag does not match')
            if (count == restart_download):
                print('\nRestarting Download Process for ' + chosen_tag)
                restart_download += 256
                download_images(count, restart_download, chosen_tag, trainer)
            # set skip_pics to higher number to search for more images

def main():
    '''
    Download Custom Vision Images that are already tagged and save them based on the tag name you choose
    '''
    trainer = get_trainer()
    tags = get_tags(trainer)
    print(tags)
    # tags = ['0 - No Features', '1 - Single Use Plastic', '2 - Chemicals', '3 - Fishing Gear', '4 - Clothing', '5 - Other Plastics / Equipment', '7 - Organic Matter']
    # Only value to change in the chosen tag based on the position in the list
    download_images(0, 256, tags[6], trainer)


if __name__ == "__main__":
    main()
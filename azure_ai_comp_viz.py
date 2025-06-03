import os
import shutil
import re
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException
from dotenv import load_dotenv

# load environment variables
load_dotenv()

subscription_key_csv = os.getenv("AZURE_COMPUTERVISION_CSV_KEY")
endpoint_csv = os.getenv("AZURE_COMPUTERVISION_CSV_ENDPOINT")

if not subscription_key_csv or not endpoint_csv:
    raise ValueError("Missing Azure Computer Vision CSV credentials in environment variables.")

# authentication
client = ComputerVisionClient(endpoint_csv, CognitiveServicesCredentials(subscription_key_csv))

image_folder = "data/images" # input folder
analysis_folder = os.path.join(image_folder, "analysis")
updated_images_folder = os.path.join(analysis_folder, "updated_images") # output folder

os.makedirs(analysis_folder, exist_ok=True)
os.makedirs(updated_images_folder, exist_ok=True)

output_file = os.path.join(analysis_folder, "analysis_results.txt")

all_outputs = []

def clean_filename(text):
    # Lowercase, replace non-alphanumeric with underscore, remove leading/trailing underscores
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def derive_filename(analysis, original_ext):
    # 1. try objects (top confidence)
    if analysis.objects and len(analysis.objects) > 0:
        top_obj = max(analysis.objects, key=lambda o: o.confidence)
        base_name = top_obj.object_property
        return clean_filename(base_name) + original_ext

    # 2. try categories (top score)
    if analysis.categories and len(analysis.categories) > 0:
        top_cat = max(analysis.categories, key=lambda c: c.score)
        return clean_filename(top_cat.name) + original_ext

    # 3. try tags (top 3 tags, excluding generic words)
    if analysis.tags and len(analysis.tags) > 0:
        generic_tags = {'indoor', 'outdoor', 'person', 'people', 'man', 'woman', 'street', 'road'}
        filtered_tags = [t.name for t in analysis.tags if t.name not in generic_tags]
        if filtered_tags:
            top_tags = filtered_tags[:3]
            return clean_filename('_'.join(top_tags)) + original_ext

    # 4. if those fail
    if analysis.description and analysis.description.captions:
        caption = analysis.description.captions[0].text
        words = caption.split()[:3]
        return clean_filename('_'.join(words)) + original_ext

    # 5. Everything fails go with the original name
    return 'image' + original_ext

for filename in os.listdir(image_folder):
    image_path = os.path.join(image_folder, filename)
    if os.path.isfile(image_path):
        print(f"Processing image: {filename}")
        all_outputs.append(f"Processing image: {filename}\n")
        try:
            with open(image_path, "rb") as image_stream:
                analysis = client.analyze_image_in_stream(
                    image=image_stream,
                    visual_features=[
                        "Categories",
                        "Tags",
                        "Description",
                        "Faces",
                        "Objects",
                        "Color",
                        "Brands",
                        "Adult"
                    ]
                )

            def log_print(text):
                print(text)
                all_outputs.append(text + "\n")

            # categories
            if analysis.categories:
                log_print(" Categories:")
                for category in analysis.categories:
                    log_print(f"  - {category.name} (Score: {category.score:.2f})")

            # tags
            if analysis.tags:
                tags_list = [tag.name for tag in analysis.tags]
                log_print(" Tags:")
                log_print(f"  - {', '.join(tags_list)}")

            # description captions
            if analysis.description and analysis.description.captions:
                log_print(" Description Captions:")
                for caption in analysis.description.captions:
                    log_print(f"  - {caption.text} (Confidence: {caption.confidence:.2f})")

            # faces
            if analysis.faces:
                log_print(" Faces:")
                for face in analysis.faces:
                    rect = face.face_rectangle
                    log_print(f"  - Age: {face.age}, Gender: {face.gender}, Rectangle: {rect}")

            # objects
            if analysis.objects:
                log_print(" Objects:")
                for obj in analysis.objects:
                    rect = obj.rectangle
                    log_print(f"  - Object: {obj.object_property}, Confidence: {obj.confidence:.2f}, Rectangle: {rect}")

            # color anlaysis
            if analysis.color:
                log_print(" Color:")
                log_print(f"  - Dominant Colors: {', '.join(analysis.color.dominant_colors)}")
                log_print(f"  - Accent Color: #{analysis.color.accent_color}")
                log_print(f"  - Is BW Image: {analysis.color.is_bw_img}")

            # find brands
            if analysis.brands:
                log_print(" Brands:")
                for brand in analysis.brands:
                    log_print(f"  - Brand: {brand.name}, Confidence: {brand.confidence:.2f}")

            # detect adult content
            if analysis.adult:
                log_print(" Adult Content:")
                log_print(f"  - Is Adult Content: {analysis.adult.is_adult_content} (Score: {analysis.adult.adult_score:.2f})")
                log_print(f"  - Is Racy Content: {analysis.adult.is_racy_content} (Score: {analysis.adult.racy_score:.2f})")

            # derive new filename and copy
            original_ext = os.path.splitext(filename)[1]
            new_filename = derive_filename(analysis, original_ext)

            # avoid overwrite by adding suffix
            candidate_name = new_filename
            counter = 1
            while os.path.exists(os.path.join(updated_images_folder, candidate_name)):
                candidate_name = f"{os.path.splitext(new_filename)[0]}_{counter}{original_ext}"
                counter += 1
            new_filename = candidate_name

            shutil.copy2(image_path, os.path.join(updated_images_folder, new_filename))
            log_print(f" Image saved as: {new_filename}")

        except ComputerVisionErrorResponseException as e:
            err_msg = f"  Skipped: Invalid image or unsupported format. ({e.message})"
            print(err_msg)
            all_outputs.append(err_msg + "\n")
        except Exception as e:
            err_msg = f"  Skipped: Unexpected error: {e}"
            print(err_msg)
            all_outputs.append(err_msg + "\n")

        all_outputs.append("\n")  # blank line between images for better formatting

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(all_outputs)

print(f"Analysis complete. Results saved to {output_file}")
print(f"Renamed images saved to folder: {updated_images_folder}")

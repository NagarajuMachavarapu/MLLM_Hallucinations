import torch
import json
from PIL import Image
import requests
import os
#from tqdm import tqdm
from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
import sys

#print(sys.argv[1])


model = InstructBlipForConditionalGeneration.from_pretrained("Salesforce/instructblip-vicuna-7b")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(device)
sys.exit()

processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")
imagesPath = "/home/smalyal2/CLEVR_v1.0/images/val/"
quesDirectory = f"/scratch/smalyal2/MLLM_Hallucinations/LanguageAugmentation/data/"

# Open the JSON file and process each line
outputFileDirectory = "/scratch/smalyal2/MLLM_Hallucinations/LanguageAugmentation/data/answers/"

for filename in os.listdir(quesDirectory):
    if filename.endswith('.json'):
        file_path = os.path.join(quesDirectory, filename)
        print(filename)
        with open(file_path, 'r') as jsonFile, open(f'{outputFileDirectory}{filename[:-5]}_results.json', 'a') as resultFile:
            res = []
            for line in jsonFile.readlines()[:1]:
                entry = json.loads(line)
                img_name = entry["image_name"]
                image_ques = entry["questions"]
        
                ansList = []  # List to store results for each question
        
                for q in image_ques:
                    img = Image.open(imagesPath + img_name).convert("RGB")
                    inputs = processor(images=img, text=q["question"], return_tensors="pt").to(device)
                    outputs = model.generate(
                        **inputs,
                        do_sample=False,
                        num_beams=5,
                        max_length=256,
                        min_length=1,
                        top_p=0.9,
                        repetition_penalty=1.5,
                        length_penalty=1.0,
                        temperature=1,
                    )
                    generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
        
                    # Append results for each question to the file
                    res.append({
                        "Image ID":img_name,
                        "Question": q["question"],
                        "q1 answer": q["q1 answer"],
                        "q2 answer": q["q2 answer"],
                        "Ground truth": q["answer"],
                        "Model generated answer": generated_text
                    })
                    # json.dump(res, resultFile)
        
                # Append results for each image to the file
            json.dump(res, resultFile)
            resultFile.close()
                #resultFile.write('\n')  # Add a newline for better readability

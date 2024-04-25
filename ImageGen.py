import os
import torch
import random
from diffusers import StableDiffusionPipeline, TCDScheduler
import numpy as np
from diffusers import DPMSolverMultistepScheduler as DefaultDPMSolver

class ImageGen:
    def __init__(self):
        # Set the environment variable to disable the warning for symlinks
        os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

        self.images_dir = "./images"  # Directory to save output images

        # Create directories if they do not exist
        os.makedirs(self.images_dir, exist_ok=True)

        tcd_lora_id = "h1t/TCD-SD15-LoRA"
        self.pipe = StableDiffusionPipeline.from_pretrained('lykon/dreamshaper-8', torch_dtype=torch.float16, variant="fp16").to("cuda")
        self.pipe.scheduler = TCDScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.load_lora_weights(tcd_lora_id)
        self.pipe.fuse_lora()
        
        self.sampling_schedule = [999, 850, 736, 645, 545, 455, 343, 233, 124,  24,   0]

    def generate_image(self, prompt, output_name):
            output_image = self.pipe(
                prompt=prompt,
                num_inference_steps=4,
                guidance_scale=0,
                eta=0.3, 
                generator=torch.Generator(device="cuda").manual_seed(random.randint(1, 100000)),
            ).images[0]
            print("Running image generation...")
            print(prompt)

            # Save the output image in the specified directory with a unique name for each image
            output_image.save(os.path.join(self.images_dir, output_name + ".png"))

# Code to execute only if this module is run directly
if __name__ == "__main__":
    image_gen = ImageGen()
    prompt = "beautiful sunset"
    image_gen.generate_image(prompt, "beautiful_sunset")
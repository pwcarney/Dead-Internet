import os
import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file


class ImageGen:
    def __init__(self):
        # Set the environment variable to disable the warning for symlinks
        os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

        model_dir = "./sd_model"  # Directory to save the model
        self.images_dir = "./images"  # Directory to save output images

        # Create directories if they do not exist
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_2step_unet.safetensors"

        # Download and load the model
        model_path = hf_hub_download(repo, ckpt, cache_dir=model_dir)
        config = UNet2DConditionModel.load_config(base, subfolder="unet")
        unet = UNet2DConditionModel.from_config(config).to("cuda", torch.float16)
        unet.load_state_dict(load_file(model_path, device="cuda"))

        # Initialize the pipeline with the downloaded model
        self.pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=unet, torch_dtype=torch.float16, variant="fp16").to("cuda")

        # Adjust the scheduler as required
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(self.pipe.scheduler.config, timestep_spacing="trailing")

    def generate_image(self, prompt, output_name):
            # Generate the image, specifying the number of inference steps and guidance scale
            output_image = self.pipe(prompt, num_inference_steps=2, guidance_scale=0).images[0]
            print("Running image generation...")
            print(prompt)

            # Save the output image in the specified directory with a unique name for each image
            output_image.save(os.path.join(self.images_dir, output_name + ".png"))

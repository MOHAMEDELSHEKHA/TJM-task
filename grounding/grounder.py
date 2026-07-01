import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
from PIL import Image
import re

MODEL_NAME = "Qwen/Qwen2-VL-7B-Instruct"

print("Loading Qwen2-VL-7B grounding model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    quantization_config=quantization_config,
    device_map="auto"
)

processor = AutoProcessor.from_pretrained(MODEL_NAME)

print("Grounding model loaded successfully.")


def ground_element(image, instruction="Find the Notepad desktop icon"):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {
                    "type": "text",
                    "text": f'In this UI screenshot, what is the position of the element corresponding to "{instruction}" (with bbox)?'
                }
            ],
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=100)

    generated_ids_trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=False,
        clean_up_tokenization_spaces=False
    )[0]

    print(f"Grounder output: {output_text}")
    return parse_coordinates(output_text)


def parse_coordinates(output_text):
    pattern = r'\((\d+),(\d+)\),\((\d+),(\d+)\)'
    match = re.search(pattern, output_text)

    if match:
        x1 = int(match.group(1))
        y1 = int(match.group(2))
        x2 = int(match.group(3))
        y2 = int(match.group(4))
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if 0 <= cx <= 1000 and 0 <= cy <= 1000:
            print(f"Grounder found: bbox ({x1},{y1}),({x2},{y2}) → center ({cx},{cy})")
            return (cx, cy)
        return None

    point_pattern = r"POINT:\s*\((\d+),\s*(\d+)\)"
    point_match = re.search(point_pattern, output_text)
    if point_match:
        x = int(point_match.group(1))
        y = int(point_match.group(2))
        if 0 <= x <= 1000 and 0 <= y <= 1000:
            if x == 500 and y == 500:
                return None
            return (x, y)

    return None


def normalized_to_pixels(norm_coords, width, height):
    norm_x, norm_y = norm_coords
    local_x = int((norm_x / 1000) * width)
    local_y = int((norm_y / 1000) * height)
    return (local_x, local_y)


def convert_to_screen_coordinates(local_coords, region):
    if local_coords is None:
        return None
    local_x, local_y = local_coords
    x1, y1, x2, y2 = region
    return (x1 + local_x, y1 + local_y)


def fine_search(screenshot, rough_coords, instruction):
    from automation.screenshot import crop_region

    cx, cy = rough_coords
    x1 = max(0, cx - 100)
    y1 = max(0, cy - 100)
    x2 = min(1920, cx + 100)
    y2 = min(1080, cy + 100)

    fine_region = (x1, y1, x2, y2)
    crop_width = x2 - x1
    crop_height = y2 - y1

    cropped = crop_region(screenshot, fine_region)
    resized = cropped.resize((448, 448))

    norm_coords = ground_element(resized, instruction)

    if norm_coords is not None:
        local_coords = normalized_to_pixels(norm_coords, crop_width, crop_height)
        screen_coords = convert_to_screen_coordinates(local_coords, fine_region)
        print(f"Fine search result: {screen_coords}")
        return screen_coords

    return None


def find_element_in_regions(screenshot, regions, instruction="Find the Notepad desktop shortcut icon"):
    from automation.screenshot import crop_region

    for i, region in enumerate(regions):
        x1, y1, x2, y2 = region
        width = x2 - x1
        height = y2 - y1

        cropped = crop_region(screenshot, region)
        resized = cropped.resize((448, 448))

        norm_coords = ground_element(resized, instruction)

        if norm_coords is not None:
            local_coords = normalized_to_pixels(norm_coords, width, height)
            rough_screen = convert_to_screen_coordinates(local_coords, region)
            print(f"Rough screen coords: {rough_screen}")

            fine_coords = fine_search(screenshot, rough_screen, instruction)
            if fine_coords is not None:
                print(f"✓ Icon found at: {fine_coords}")
                return fine_coords, region

            print(f"✓ Icon found at: {rough_screen}")
            return rough_screen, region

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        print(f"Grounder failed — using region center: ({center_x}, {center_y})")
        return (center_x, center_y), region

    return None, None
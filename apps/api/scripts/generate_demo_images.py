"""
Demo Property Photo Generator
=============================
Generates sample property photos for testing AI Property Doctor

For demo purposes - In production, users upload real photos
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_images():
    """Create sample property images for demo"""

    output_dir = "/tmp/ecoimmo_demo_images"
    os.makedirs(output_dir, exist_ok=True)

    # Sample 1: Good property (Modern, double glazing)
    img1 = Image.new('RGB', (800, 600), color=(230, 230, 230))
    draw1 = ImageDraw.Draw(img1)

    # Draw modern windows (double glazing appearance)
    for i in range(3):
        x = 100 + i * 250
        draw1.rectangle([x, 150, x+150, 400], fill=(180, 210, 230), outline=(50, 50, 50), width=3)
        draw1.rectangle([x+5, 155, x+145, 395], fill=(200, 220, 240), outline=(100, 100, 100), width=1)

    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    draw1.text((250, 50), "DEMO: Modern Apartment", fill=(0, 0, 0), font=font)
    draw1.text((200, 480), "Double Glazing • Good Insulation", fill=(0, 128, 0), font=font)

    img1.save(f"{output_dir}/good_property.jpg")
    print(f"✅ Created: {output_dir}/good_property.jpg")


    # Sample 2: Poor property (Old, single glazing)
    img2 = Image.new('RGB', (800, 600), color=(200, 190, 180))
    draw2 = ImageDraw.Draw(img2)

    # Draw old windows (single glazing)
    for i in range(3):
        x = 100 + i * 250
        draw2.rectangle([x, 150, x+150, 400], fill=(160, 160, 170), outline=(80, 80, 80), width=2)
        # Add cracks
        draw2.line([x+50, 150, x+70, 400], fill=(50, 50, 50), width=2)

    draw2.text((250, 50), "DEMO: Old Apartment", fill=(0, 0, 0), font=font)
    draw2.text((180, 480), "Single Glazing • Poor Insulation", fill=(200, 0, 0), font=font)

    img2.save(f"{output_dir}/poor_property.jpg")
    print(f"✅ Created: {output_dir}/poor_property.jpg")


    # Sample 3: Average property
    img3 = Image.new('RGB', (800, 600), color=(220, 220, 210))
    draw3 = ImageDraw.Draw(img3)

    # Draw average windows
    for i in range(3):
        x = 100 + i * 250
        draw3.rectangle([x, 150, x+150, 400], fill=(190, 200, 210), outline=(70, 70, 70), width=2)
        draw3.rectangle([x+3, 153, x+147, 397], fill=(200, 210, 220), outline=(90, 90, 90), width=1)

    draw3.text((250, 50), "DEMO: Average Apartment", fill=(0, 0, 0), font=font)
    draw3.text((200, 480), "Double Glazing • Average Condition", fill=(128, 128, 0), font=font)

    img3.save(f"{output_dir}/average_property.jpg")
    print(f"✅ Created: {output_dir}/average_property.jpg")

    print(f"\n📁 Demo images saved to: {output_dir}")
    print("Use these images to test the AI Property Doctor!")

    return output_dir

if __name__ == "__main__":
    create_demo_images()

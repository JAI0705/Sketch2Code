import os
import shutil

# Define your folder paths
base_dir = "sketch2code_dataset_v1"
webpages_dir = os.path.join(base_dir, "webpages")
sketches_dir = os.path.join(base_dir, "sketches")

# Ensure target directory exists
os.makedirs(sketches_dir, exist_ok=True)

# Define image extensions
image_extensions = ('.png', '.jpg', '.jpeg', '.webp')

# Step 1: Move image files from webpages/ to sketches/
moved = 0
for filename in os.listdir(webpages_dir):
    if filename.lower().endswith(image_extensions):
        src_path = os.path.join(webpages_dir, filename)
        dest_path = os.path.join(sketches_dir, filename)

        if not os.path.exists(dest_path):  # Avoid overwriting
            shutil.move(src_path, dest_path)
            print(f"✅ Moved: {filename}")
            moved += 1
        else:
            print(f"⚠️ Already exists in sketches/: {filename} — skipped")

print(f"\n📦 Done moving. Total {moved} image(s) moved to 'sketches/' folder.\n")

# Step 2: Check how many sketch images have a matching .html
sketch_files = [f for f in os.listdir(sketches_dir) if f.endswith('.png')]
html_ids = {f.split('.')[0] for f in os.listdir(webpages_dir) if f.endswith('.html')}

matched = 0
unmatched = []

for sketch in sketch_files:
    sketch_id = sketch.split('_')[0]  # assumes sketch name is like "1234_*.png"
    if sketch_id in html_ids:
        matched += 1
    else:
        unmatched.append(sketch)

print(f"🔍 Matched {matched}/{len(sketch_files)} sketch images with existing HTML files.")
if unmatched:
    print(f"⚠️ Unmatched sketch images (no corresponding HTML):")
    for u in unmatched:
        print(f" - {u}")

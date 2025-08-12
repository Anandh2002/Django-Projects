import easyocr
import pandas as pd
from collections import defaultdict

# Path to your image file
image_path = 'Media.jpg'

# Initialize EasyOCR Reader (English)
reader = easyocr.Reader(['en'], gpu=False)

# Extract text with bounding boxes (detail=1)
results = reader.readtext(image_path, detail=1)

# Function to get the vertical midpoint of a bounding box
def get_mid_y(box):
    ys = [point[1] for point in box]
    return sum(ys) / len(ys)

# Group detected text by rows based on vertical proximity
rows = defaultdict(list)
y_threshold = 10  # Adjust if rows are merged or split incorrectly

for bbox, text, _ in results:
    mid_y = get_mid_y(bbox)
    found_row = False
    for key in rows:
        if abs(key - mid_y) < y_threshold:
            rows[key].append((bbox, text))
            found_row = True
            break
    if not found_row:
        rows[mid_y].append((bbox, text))

# Sort rows top to bottom
sorted_row_keys = sorted(rows.keys())

table_data = []
for key in sorted_row_keys:
    row = rows[key]
    # Sort each row's text left to right
    row_sorted = sorted(row, key=lambda x: min([point[0] for point in x[0]]))
    texts = [t[1] for t in row_sorted]
    table_data.append(texts)

# Parse rows to columns: SI, ITEM NUMBER, QTY, AMOUNT
parsed_rows = []
for row in table_data:
    # Skip rows that are too short or look like headers
    if len(row) < 4:
        continue
    # If exactly 4 columns, assign directly
    if len(row) == 4:
        si, item_number, qty, amount = row
    else:
        # If more than 4 columns, assume:
        # SI = first element
        # QTY = second last
        # AMOUNT = last
        # ITEM NUMBER = everything in between joined by space
        si = row[0]
        qty = row[-2]
        amount = row[-1]
        item_number = ' '.join(row[1:-2])
    parsed_rows.append([si, item_number, qty, amount])

# Create DataFrame and save to Excel
df = pd.DataFrame(parsed_rows, columns=['SI', 'ITEM NUMBER', 'QTY', 'AMOUNT'])
output_excel = 'extracted_table_easyocr_final.xlsx'
df.to_excel(output_excel, index=False)

print(f"Data extracted and saved to {output_excel}")

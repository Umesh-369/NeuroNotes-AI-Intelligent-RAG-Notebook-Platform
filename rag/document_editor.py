import os
import io
from pypdf import PdfReader, PdfWriter
from PIL import Image

def extract_images_to_pdf(document_id: int, notebook_id: int, filepath: str) -> tuple[str, str]:
    """
    Extracts all images from a PDF and saves them to a new PDF.
    Returns the filepath of the new PDF, or None if no images were found.
    """
    reader = PdfReader(filepath)
    images = []
    
    for page in reader.pages:
        for image_file_object in page.images.values():
            try:
                # Open the image using PIL
                img = Image.open(io.BytesIO(image_file_object.data))
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                print(f"Failed to process an image on page: {e}")
                
    if not images:
        return None, None
        
    # Generate new filename
    safe_title = f"images_from_doc_{document_id}.pdf"
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    upload_folder = os.path.join(root_dir, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    out_filepath = os.path.join(upload_folder, f"derived_{notebook_id}_{safe_title}")
    
    # Save first image and append the rest as a single PDF
    images[0].save(out_filepath, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
    
    return out_filepath, safe_title


def edit_pdf_pages(document_id: int, notebook_id: int, filepath: str, remove_pages: list[int], overwrite: bool = False) -> tuple[str, str]:
    """
    Removes the specified 1-based page indices from the PDF.
    If overwrite is True, it modifies the file in place.
    If overwrite is False, saves to a new file and returns the new filepath.
    Returns (out_filepath, out_filename)
    """
    reader = PdfReader(filepath)
    writer = PdfWriter()
    
    # Convert from 1-based indexing passed by user to 0-based indexing
    remove_indices = {p - 1 for p in remove_pages}
    
    for i, page in enumerate(reader.pages):
        if i not in remove_indices:
            writer.add_page(page)
            
    if len(writer.pages) == 0:
        raise ValueError("Cannot remove all pages from the document.")

    if overwrite:
        out_filepath = filepath
        out_filename = os.path.basename(filepath)
    else:
        out_filename = f"edited_doc_{document_id}.pdf"
        root_dir = os.path.dirname(os.path.dirname(__file__))
        upload_folder = os.path.join(root_dir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        out_filepath = os.path.join(upload_folder, f"derived_{notebook_id}_{out_filename}")
    
    with open(out_filepath, 'wb') as f:
        writer.write(f)
        
    return out_filepath, out_filename

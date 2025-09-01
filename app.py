from flask import Flask, render_template, request, jsonify, send_file
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import json
import base64
import os
import io
import tempfile
import time
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Rendering home page")
    return render_template('index.html')

# @app.route('/save-to-drive', methods=['POST'])
# def save_to_drive():
#     try:
#         data = request.get_json()
#         logger.info(f"Received data for save-to-drive: {data['mission1']['zone']}")
        
#         SCOPES = ['https://www.googleapis.com/auth/drive.file']
#         SERVICE_ACCOUNT_FILE = 'credentials.json'
#         credentials = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#         drive_service = build('drive', 'v3', credentials=credentials)
#         FOLDER_ID = '1HNpd-704g6TiZPhRc4JjK5jVFSEip4cB'
        
#         game_data_json = json.dumps(data, ensure_ascii=False)
#         json_file_name = f"explorer_card_{data['mission1']['zone']}_{int(time.time())}.json"
        
#         json_metadata = {
#             'name': json_file_name,
#             'parents': [FOLDER_ID],
#             'mimeType': 'application/json'
#         }
        
#         json_media = MediaFileUpload(
#             io.BytesIO(game_data_json.encode('utf-8')),
#             mimetype='application/json'
#         )
        
#         drive_service.files().create(
#             body=json_metadata,
#             media_body=json_media,
#             fields='id'
#         ).execute()
        
#         for mission, mission_data in data.items():
#             if 'screenshot' in mission_data and mission_data['screenshot']:
#                 try:
#                     screenshot_data = mission_data['screenshot'].split(',')[1]
#                     screenshot_bytes = base64.b64decode(screenshot_data)
#                     screenshot_file_name = f"{mission}_screenshot_{data['mission1']['zone']}_{int(time.time())}.png"
                    
#                     screenshot_metadata = {
#                         'name': screenshot_file_name,
#                         'parents': [FOLDER_ID],
#                         'mimeType': 'image/png'
#                     }
                    
#                     screenshot_media = MediaFileUpload(
#                         io.BytesIO(screenshot_bytes),
#                         mimetype='image/png'
#                     )
                    
#                     drive_service.files().create(
#                         body=screenshot_metadata,
#                         media_body=screenshot_media,
#                         fields='id'
#                     ).execute()
#                     logger.info(f"Saved screenshot {screenshot_file_name} to Google Drive")
#                 except Exception as e:
#                     logger.error(f"Error saving screenshot for {mission}: {str(e)}")
#                     raise
                
#         return jsonify({'message': 'Data successfully saved to Google Drive!'}), 200
    
#     except Exception as e:
#         logger.error(f"Error in save-to-drive: {str(e)}")
#         return jsonify({'error': str(e)}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        logger.info(f"Generating PDF for zone: {data['mission1']['zone']}")
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {temp_dir}")
        
        try:
            # Save screenshots to temporary files
            mission1_screenshot = None
            mission2_screenshot = None
            
            if data['mission1']['screenshot']:
                try:
                    mission1_data = data['mission1']['screenshot'].split(',')[1]
                    mission1_bytes = base64.b64decode(mission1_data)
                    mission1_path = os.path.join(temp_dir, 'mission1.png')
                    with open(mission1_path, 'wb') as f:
                        f.write(mission1_bytes)
                    if os.path.exists(mission1_path):
                        logger.debug(f"Saved mission1 screenshot to {mission1_path}")
                        mission1_screenshot = mission1_path
                    else:
                        logger.error(f"Failed to save mission1 screenshot to {mission1_path}")
                        raise Exception("Failed to save mission1 screenshot")
                except Exception as e:
                    logger.error(f"Error processing mission1 screenshot: {str(e)}")
                    raise
                
            if data['mission2']['screenshot']:
                try:
                    mission2_data = data['mission2']['screenshot'].split(',')[1]
                    mission2_bytes = base64.b64decode(mission2_data)
                    mission2_path = os.path.join(temp_dir, 'mission2.png')
                    with open(mission2_path, 'wb') as f:
                        f.write(mission2_bytes)
                    if os.path.exists(mission2_path):
                        logger.debug(f"Saved mission2 screenshot to {mission2_path}")
                        mission2_screenshot = mission2_path
                    else:
                        logger.error(f"Failed to save mission2 screenshot to {mission2_path}")
                        raise Exception("Failed to save mission2 screenshot")
                except Exception as e:
                    logger.error(f"Error processing mission2 screenshot: {str(e)}")
                    raise
            
            # Create PDF with reportlab
            pdf_file = os.path.join(temp_dir, 'explorer_card.pdf')
            pdf_file = os.path.normpath(pdf_file)  # Normalize path for Windows
            c = canvas.Canvas(pdf_file, pagesize=A4)
            width, height = A4  # A4 dimensions in points (595 x 842)
            
            # Title and header
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width / 2, height - 50, "Carte d'Explorateur")
            c.setFont("Helvetica", 18)
            c.drawCentredString(width / 2, height - 80, "Pont de Khaznadar")
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 110, "Félicitations, Explorateur !")
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, height - 140, "Tu as complété toutes les missions et découvert les secrets du pont de Khaznadar.")
            
            # Mission 1: Cherche et Ressens
            y_position = height - 180
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Mission 1 : Cherche et Ressens")
            y_position -= 20
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position, f"Zone explorée : {data['mission1']['zone'].capitalize()}")
            y_position -= 20
            c.drawString(50, y_position, f"Émotions placées : {len(data['mission1']['emotions'])} émotion(s)")
            y_position -= 30
            
            # Add Mission 1 screenshot
            if mission1_screenshot:
                try:
                    img = ImageReader(mission1_screenshot)
                    img_width, img_height = img.getSize()
                    aspect = img_height / float(img_width)
                    target_width = min(width - 100, 500)  # Max width with margins
                    target_height = target_width * aspect
                    if y_position - target_height < 50:
                        c.showPage()  # Start new page if not enough space
                        y_position = height - 50
                    c.drawImage(img, 50, y_position - target_height, width=target_width, height=target_height)
                    y_position -= target_height + 20
                    c.drawString(50, y_position, "Capture d'écran de la Mission 1")
                    y_position -= 30
                except Exception as e:
                    logger.error(f"Error adding mission1 screenshot to PDF: {str(e)}")
                    c.drawString(50, y_position, "Erreur : Impossible d'inclure la capture d'écran de la Mission 1")
                    y_position -= 30
            
            # Add Mission 1 comments
            if data['mission1']['reason']:
                c.drawString(50, y_position, "Commentaires :")
                y_position -= 20
                c.setFont("Helvetica-Oblique", 12)
                # Split long text into lines
                lines = data['mission1']['reason'].split('\n')
                for line in lines:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                    c.drawString(50, y_position, line[:80])  # Truncate to fit page
                    y_position -= 20
                c.setFont("Helvetica", 12)
                y_position -= 10
            
            # Mission 2: Transforme le Pont
            c.setFont("Helvetica-Bold", 14)
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, "Mission 2 : Transforme le Pont")
            y_position -= 20
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position, f"Éléments de transformation : {len(data['mission2']['elements'])} ajout(s)")
            y_position -= 30
            
            # Add Mission 2 screenshot
            if mission2_screenshot:
                try:
                    img = ImageReader(mission2_screenshot)
                    img_width, img_height = img.getSize()
                    aspect = img_height / float(img_width)
                    target_width = min(width - 100, 500)
                    target_height = target_width * aspect
                    if y_position - target_height < 50:
                        c.showPage()
                        y_position = height - 50
                    c.drawImage(img, 50, y_position - target_height, width=target_width, height=target_height)
                    y_position -= target_height + 20
                    c.drawString(50, y_position, "Capture d'écran de la Mission 2")
                    y_position -= 30
                except Exception as e:
                    logger.error(f"Error adding mission2 screenshot to PDF: {str(e)}")
                    c.drawString(50, y_position, "Erreur : Impossible d'inclure la capture d'écran de la Mission 2")
                    y_position -= 30
            
            # Finalize PDF
            c.showPage()
            c.save()
            
            # Verify PDF exists
            if not os.path.exists(pdf_file):
                logger.error(f"PDF file not found at {pdf_file}")
                raise Exception(f"PDF file not found at {pdf_file}")
            
            logger.info(f"PDF generated successfully at {pdf_file}")
            
            # Move PDF to a stable location to avoid cleanup
            stable_pdf_file = os.path.join(tempfile.gettempdir(), f"explorer_card_{data['mission1']['zone']}_{int(time.time())}.pdf")
            shutil.copy(pdf_file, stable_pdf_file)
            logger.debug(f"Copied PDF to stable location: {stable_pdf_file}")
            
            # Ensure file is readable
            if not os.access(stable_pdf_file, os.R_OK):
                logger.error(f"PDF file at {stable_pdf_file} is not readable")
                raise Exception(f"PDF file at {stable_pdf_file} is not readable")
            
            return send_file(
                stable_pdf_file,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"carte_explorateur_{data['mission1']['zone']}.pdf"
            )
        
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
    
    except Exception as e:
        logger.error(f"Error in generate-pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
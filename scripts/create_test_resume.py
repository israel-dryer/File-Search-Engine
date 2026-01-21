
import os
from reportlab.pdfgen import canvas

def create_resume():
    output_dir = os.path.join("data", "test_resume")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    path = os.path.join(output_dir, "Siddhesh_Resume.pdf")
    c = canvas.Canvas(path)
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Siddhesh Student")
    c.setFont("Helvetica", 12)
    c.drawString(100, 735, "Email: siddhesh@example.com | Phone: +91-9876543210")
    
    # Education Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 700, "Education")
    c.line(100, 695, 500, 695)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 675, "Indian Institute of Technology, Bombay (IIT Bombay)")
    c.setFont("Helvetica", 12)
    c.drawString(100, 660, "Bachelor of Technology in Computer Science")
    c.drawString(400, 660, "2022 - 2026")
    
    # Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 620, "Skills")
    c.line(100, 615, 500, 615)
    c.setFont("Helvetica", 12)
    c.drawString(100, 595, "Languages: Python, JavaScript, C++")
    c.drawString(100, 580, "Frameworks: React, FastAPI, TensorFlow")
    
    c.save()
    print(f"Created resume at: {path}")

if __name__ == "__main__":
    create_resume()

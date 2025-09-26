from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from django.http import HttpResponse,HttpResponseNotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import re
from rest_framework.permissions import AllowAny

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        extracted_text = page.extract_text()
        text += extracted_text if extracted_text else ""
    return text.replace('\n', ' ').strip()

def extract_text_from_image(image_file):
    extracted_text = pytesseract.image_to_string(Image.open(image_file))
    return extracted_text.replace('\n', ' ').strip()

@api_view(['POST'])
@permission_classes((AllowAny,))
def verify_files(request):
    serializer = VerificationSerializer(data=request.data)
    if serializer.is_valid():
        source_file = request.FILES['source_file']
        target_file = request.FILES['target_file']

        # Extract text from files
        source_text = extract_text_from_pdf(source_file) if source_file.name.endswith('.pdf') else extract_text_from_image(source_file)
        target_text = extract_text_from_pdf(target_file) if target_file.name.endswith('.pdf') else extract_text_from_image(target_file)

        # Debugging: Print extracted text
        print("Source File Text:", source_text)
        print("Target File Text:", target_text)

        # Extract reference number and amount from source text
        source_ref, source_amount = extract_ref_and_amount(source_text)
        target_ref_matches = find_ref_in_target(target_text, source_ref)

        # Validate if the reference number and amount match
        success = False
        if target_ref_matches:
            success = any(source_amount in match for match in target_ref_matches)

        return Response({
            'success': success,
            'source_ref': source_ref,
            'source_amount': source_amount,
            'target_ref_matches': target_ref_matches
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def extract_ref_and_amount(text):
    """Extract reference number and amount from the source text."""
    ref_pattern = r"REF\d+"  # Pattern for reference number
    amount_pattern = r"\d+\.\d{2}"  # Pattern for amount
    ref = re.search(ref_pattern, text)
    amount = re.search(amount_pattern, text)
    return ref.group(0) if ref else None, amount.group(0) if amount else None

def find_ref_in_target(text, ref):
    """Find matches for the reference number in the target text."""
    return re.findall(rf"{ref}.*", text) if ref else []

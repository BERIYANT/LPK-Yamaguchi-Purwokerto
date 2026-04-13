from utils.pdf_generator import generate_registration_pdf
try:
    res = generate_registration_pdf({})
    print(type(res), len(res))
except Exception as e:
    print("Error:", e)

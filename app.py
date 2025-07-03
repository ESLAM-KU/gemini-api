from flask import Flask, request, jsonify
import google.generativeai as genai
import mimetypes

app = Flask(__name__)

# إعداد مفتاح API
genai.configure(api_key="AIzaSyB4Rf8wINhYnBkeyQO_NKPHhh2WyotEDTs")
model = genai.GenerativeModel("gemini-2.5-flash")

@app.before_request
def show_routes():
    print(f"Incoming request to {request.path}")

@app.route('/')
def home():
    return """
    <h2>✅ Gemini API is Running!</h2>
    <p>Use <code>/extract</code> endpoint with POST method and image file.</p>
    """

@app.route('/extract', methods=['POST'])
def extract_info():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    mime_type, _ = mimetypes.guess_type(image_file.filename)

    if mime_type is None or not mime_type.startswith("image/"):
        return jsonify({'error': 'Unsupported file type'}), 400

    image_bytes = image_file.read()

    prompt = """
    استخرج بدقة من صورة البطاقة البيانات التالية فقط، واطبعها بهذا التنسيق وبدون شرح:

    الاسم الاول: [الاسم الأول فقط]
    الاسم الثاني: [جميع الأسماء التالية بعد الاسم الأول، كما هي تماماً في الصورة]
    العنوان: [عنوان السكن فقط كما هو]
    الرقم القومي: [الرقم القومي كما هو]

    ملاحظة: لا تقم بشرح أو تفسير، فقط أرجع القيم كما هي من البطاقة.
    """

    try:
        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": image_bytes
            }
        ])
        result_text = (response.text or "").strip()

        result = {}
        for line in result_text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

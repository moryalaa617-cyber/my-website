from flask import Flask, request, jsonify
from flask_cors import CORS # سنحتاج هذه المكتبة للسماح بالاتصال من Netlify
import google.generativeai as genai
import markdown

app = Flask(__name__)
# تفعيل CORS للسماح بالطلبات من أي مصدر (يمكن تقييده لاحقاً)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_article():
    # استقبال البيانات من الطلب
    prompt_text = request.form.get('prompt')
    api_key = request.form.get('api_key')

    if not api_key:
        return jsonify({'error': 'لم يتم توفير مفتاح الـ API.'}), 400
    if not prompt_text:
        return jsonify({'error': 'لم يتم تقديم أي نص.'}), 400

    try:
        # إعداد Gemini باستخدام المفتاح الذي أرسله المستخدم
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        full_prompt = f"اكتب مقالاً صحفياً احترافياً باللغة العربية حول الموضوع التالي: '{prompt_text}'"

        response = model.generate_content(full_prompt)

        html_article = markdown.markdown(response.text)

        return jsonify({'article': html_article})

    except Exception as e:
        # إرجاع رسالة خطأ مفصلة للمساعدة في التشخيص
        error_message = str(e)
        print(f"ERROR during generation: {error_message}")
        # التحقق من أخطاء المصادقة الشائعة
        if "API_KEY_INVALID" in error_message or "permission" in error_message.lower():
            return jsonify({'error': 'مفتاح الـ API غير صالح أو لا يملك الصلاحية اللازمة.'}), 401

        return jsonify({'error': f'حدث خطأ داخلي في الخادم: {error_message}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

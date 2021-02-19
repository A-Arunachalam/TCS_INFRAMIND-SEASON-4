from flask import Flask, request, render_template_string,redirect,send_from_directory, jsonify
from flask import render_template, url_for, Response
import os
import cv2
from camera import VideoCamera
from ocr_core import ocr_core
from textblob import TextBlob
import gtts
from playsound import playsound
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import nltk 
nltk.download('stopwords')
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 
import matplotlib.pyplot as plt





ALLOWED_EXTENSIONS = set(["mp4", "webm", "ogg",'png', 'jpg', 'JPG','jpeg'])
UPLOAD_FOLDER = 'C:/Users/Arunachalam/ocr_server/static1/'

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
  

    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')

        if file and allowed_file(file.filename):
            filename = file.filename
            box = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print = f'Filename:{ filename }'
            return  render_template("success.html", name = filename)      

    
    return render_template('upload.html')  




def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(VideoCamera()))




files = []
@app.route('/frame', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('pic.html', msg='No file selected')
        file = request.files['file']

        # if no file is selected
        if file.filename == '':
            return render_template('pic.html', msg='No file selected')

        if file and allowed_file(file.filename):

            # call the OCR function on it
            extracted_text = ocr_core(file)
            files.append(extracted_text)

            
        with open('extract_text.txt', 'w') as f:
             f.write(extracted_text)

        file.save('C:\\Users\\Arunachalam\\ocr_server\\static1\\'+file.filename)        
 
       
       
            # extract the text and display it
        return render_template('pic.html',msg='Successfully processed',extracted_text=extracted_text,img_src= file.filename)
            
            
    elif request.method == 'GET':
        return render_template('pic.html')

@app.route('/audio')
def audio():
    file = open("extract_text.txt", "r").read().replace("\n", " ")
    tts = gtts.gTTS(file)
    tts.save("TEXT.mp3")
    playsound("TEXT.mp3")
    
    return render_template('audio.html')


@app.route('/analysis')
def analysis():
    sentence = open("extract_text.txt", "r").read().replace("\n", " ")
    sid_obj = SentimentIntensityAnalyzer() 
    sentiment_dict = sid_obj.polarity_scores(sentence) 
    print(sentiment_dict)
    labels = ['negative', 'neutral', 'positive']
    sizes  = [sentiment_dict['neg'], sentiment_dict['neu'], sentiment_dict['pos']]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%') # autopct='%1.1f%%' gives you percentages printed in every slice.
    plt.axis('equal')  # Ensures that pie is drawn as a circle.
    #plt.show()
    plt.savefig('foo.png')
    return render_template('analysis.html',text=sentiment_dict)
    
 
    
@app.route('/summary')
def summary():
    stopWords = set(stopwords.words("english")) 
    text = open("extract_text.txt", "r").read().replace("\n", " ")
    words = word_tokenize(text) 

    freqTable = dict() 
    for word in words: 
        word = word.lower() 
        if word in stopWords: 
             continue
        if word in freqTable: 
            freqTable[word] += 1
        else: 
            freqTable[word] = 1

    sentences = sent_tokenize(text) 
    sentenceValue = dict() 

    for sentence in sentences: 
        for word, freq in freqTable.items(): 
            if word in sentence.lower(): 
                if sentence in sentenceValue: 
                    sentenceValue[sentence] += freq 
                else: 
                    sentenceValue[sentence] = freq 



    sumValues = 0
    for sentence in sentenceValue: 
        sumValues += sentenceValue[sentence] 


    average = int(sumValues / len(sentenceValue)) 

    summary = '' 
    for sentence in sentences: 
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)): 
            summary += " " + sentence 
    print(summary) 
    
    return render_template('summary.html',text=summary)


if __name__ == '__main__':
     app.run(port=5002, debug=True)

    # Serve the app with gevent
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()



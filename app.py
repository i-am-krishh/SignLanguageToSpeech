# Importing packages
import numpy as np
import math
import cv2

import os, sys
import traceback
import pyttsx3
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
from string import ascii_uppercase
import enchant
from tkinter import ttk  # Add ttk import for Combobox

ddd = enchant.Dict("en-US")
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
import tkinter as tk
from PIL import Image, ImageTk

# Configuration and Environment Setup
offset = 29
os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"


# Main Application Class
class Application:

    def __init__(self):
        # Initialize language dictionary and other variables
        self.languages = {
            "मराठी (Marathi)": "mr",
            "हिंदी (Hindi)": "hi",
            "ગુજરાતી (Gujarati)": "gu",
            "বাংলা (Bengali)": "bn",
            "ਪੰਜਾਬੀ (Punjabi)": "pa",
            "தமிழ் (Tamil)": "ta",
            "తెలుగు (Telugu)": "te",
            "ಕನ್ನಡ (Kannada)": "kn",
            "മലയാളം (Malayalam)": "ml",
            "ଓଡ଼ିଆ (Odia)": "or"
        }

        # Initialize video capture and other resources
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.model = load_model('trainedModel.h5')
        
        # Initialize text-to-speech engine
        self.speak_engine = pyttsx3.init()
        self.speak_engine.setProperty("rate", 150)  # Default rate
        self.speak_engine.setProperty("volume", 1.0)  # Default volume
        self.voices = self.speak_engine.getProperty("voices")
        self.current_voice = self.voices[0]  # Default to first voice
        self.speak_engine.setProperty("voice", self.current_voice.id)

        # Initialize counters and variables
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        self.space_flag = False
        self.next_flag = True
        self.prev_char = ""
        self.count = -1
        self.ten_prev_char = []
        for i in range(10):
            self.ten_prev_char.append(" ")
        for i in ascii_uppercase:
            self.ct[i] = 0

        # Setup main window
        self.root = tk.Tk()
        self.root.title("Sign Language To Speech Conversion")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("1100x700")  # Reduced window size
        self.root.configure(bg='#f0f0f0')
        
        # Create main title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        self.T = tk.Label(title_frame, text="Sign Language To Speech Conversion", 
                         font=("Josefin Sans", 26, "bold"), bg='#f0f0f0')  # Reduced font size
        self.T.pack(pady=5)

        # Create main content frame
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Left frame for video feed
        left_frame = tk.Frame(content_frame, bg='#f0f0f0', relief='ridge', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        video_label = tk.Label(left_frame, text="Camera Feed", font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        video_label.pack(pady=5)
        
        self.panel = tk.Label(left_frame, width=300, height=300)  # Fixed size for camera feed
        self.panel.pack(padx=10, pady=5)

        # Right frame for hand skeleton and controls
        right_frame = tk.Frame(content_frame, bg='#f0f0f0', relief='ridge', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        skeleton_label = tk.Label(right_frame, text="Hand Skeleton", font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        skeleton_label.pack(pady=5)
        
        self.panel2 = tk.Label(right_frame, width=300, height=300)  # Fixed size for hand skeleton
        self.panel2.pack(padx=10, pady=5)

        # Character detection frame
        char_frame = tk.Frame(right_frame, bg='#f0f0f0')
        char_frame.pack(fill='x', padx=10, pady=5)
        
        self.T1 = tk.Label(char_frame, text="Character:", font=("Josefin Sans", 22, "bold"), bg='#f0f0f0')
        self.T1.pack(side='left', padx=5)
        
        self.panel3 = tk.Label(char_frame, font=("Josefin Sans", 22), bg='#f0f0f0')
        self.panel3.pack(side='left')

        # Bottom frame for translations and controls
        bottom_frame = tk.Frame(self.root, bg='#f0f0f0', relief='ridge', bd=2)
        bottom_frame.pack(fill='x', padx=10, pady=5)

        # Language selection frame
        lang_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        lang_frame.pack(fill='x', padx=10, pady=5)
        
        self.lang_label = tk.Label(lang_frame, text="Select Language:", 
                                 font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        self.lang_label.pack(side='left', padx=5)
        
        self.lang_var = tk.StringVar()
        self.lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                        state="readonly", font=("Josefin Sans", 12))
        self.lang_dropdown['values'] = list(self.languages.keys())
        self.lang_dropdown.set("मराठी (Marathi)")
        self.lang_dropdown.pack(side='left', padx=5)
        self.lang_dropdown.bind('<<ComboboxSelected>>', self.on_language_change)

        # Voice settings frame
        voice_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        voice_frame.pack(fill='x', padx=10, pady=5)
        
        # Voice selector
        voice_label = tk.Label(voice_frame, text="Voice:", font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        voice_label.pack(side='left', padx=5)
        
        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, 
                                         state="readonly", font=("Josefin Sans", 12), width=20)
        voice_names = [f"{v.name} ({v.gender})" for v in self.voices]
        self.voice_dropdown['values'] = voice_names
        self.voice_dropdown.set(voice_names[0])
        self.voice_dropdown.pack(side='left', padx=5)
        self.voice_dropdown.bind('<<ComboboxSelected>>', self.on_voice_change)
        
        # Speech rate control
        rate_label = tk.Label(voice_frame, text="Rate:", font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        rate_label.pack(side='left', padx=5)
        
        self.rate_scale = ttk.Scale(voice_frame, from_=50, to=300, orient='horizontal',
                                  length=150, value=150)
        self.rate_scale.pack(side='left', padx=5)
        self.rate_scale.bind("<ButtonRelease-1>", self.on_rate_change)
        
        # Volume control
        volume_label = tk.Label(voice_frame, text="Volume:", font=("Josefin Sans", 14, "bold"), bg='#f0f0f0')
        volume_label.pack(side='left', padx=5)
        
        self.volume_scale = ttk.Scale(voice_frame, from_=0, to=1, orient='horizontal',
                                    length=150, value=1.0)
        self.volume_scale.pack(side='left', padx=5)
        self.volume_scale.bind("<ButtonRelease-1>", self.on_volume_change)

        # Translation frame
        trans_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        trans_frame.pack(fill='x', padx=10, pady=5)
        
        # English text
        eng_frame = tk.Frame(trans_frame, bg='#f0f0f0')
        eng_frame.pack(fill='x', pady=5)
        
        self.T3 = tk.Label(eng_frame, text="English:", font=("Josefin Sans", 22, "bold"), bg='#f0f0f0')
        self.T3.pack(side='left', padx=5)
        
        self.panel5 = tk.Label(eng_frame, font=("Josefin Sans", 22), bg='#f0f0f0', wraplength=800)
        self.panel5.pack(side='left', padx=5)

        # Regional language text
        reg_frame = tk.Frame(trans_frame, bg='#f0f0f0')
        reg_frame.pack(fill='x', pady=5)
        
        self.T5 = tk.Label(reg_frame, text="मराठी:", font=("Josefin Sans", 22, "bold"), bg='#f0f0f0')
        self.T5.pack(side='left', padx=5)
        
        self.panel6 = tk.Label(reg_frame, font=("Josefin Sans", 22), bg='#f0f0f0', wraplength=800)
        self.panel6.pack(side='left', padx=5)

        # Control buttons frame
        button_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        button_width = 10
        button_font = ("Josefin Sans", 14)
        
        self.speak = tk.Button(button_frame, text="English\nSpeak", font=button_font,
                             command=self.speak_fun, width=button_width)
        self.speak.pack(side='left', padx=5)
        
        self.translate = tk.Button(button_frame, text="Translate", font=button_font,
                                 command=self.translate_fun, width=button_width)
        self.translate.pack(side='left', padx=5)
        
        self.speak_regional = tk.Button(button_frame, text="Regional\nSpeak", font=button_font,
                                      command=self.speak_regional_fun, width=button_width)
        self.speak_regional.pack(side='left', padx=5)
        
        self.clear = tk.Button(button_frame, text="Clear", font=button_font,
                             command=self.clear_fun, width=button_width)
        self.clear.pack(side='left', padx=5)

        # Suggestions frame
        suggest_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        suggest_frame.pack(fill='x', padx=10, pady=5)
        
        self.T4 = tk.Label(suggest_frame, text="Suggestions:", fg="red",
                          font=("Josefin Sans", 22, "bold"), bg='#f0f0f0')
        self.T4.pack(side='left', padx=5)
        
        # Suggestion buttons with background color and border
        suggestion_style = {
            'font': ("Josefin Sans", 18),
            'bg': '#e0e0e0',
            'relief': 'raised',
            'width': 15,
            'height': 1
        }
        
        self.b1 = tk.Button(suggest_frame, command=self.action1, **suggestion_style)
        self.b1.pack(side='left', padx=5)
        
        self.b2 = tk.Button(suggest_frame, command=self.action2, **suggestion_style)
        self.b2.pack(side='left', padx=5)
        
        self.b3 = tk.Button(suggest_frame, command=self.action3, **suggestion_style)
        self.b3.pack(side='left', padx=5)
        
        self.b4 = tk.Button(suggest_frame, command=self.action4, **suggestion_style)
        self.b4.pack(side='left', padx=5)

        # Initialize other variables
        self.str = " "
        self.ccc = 0
        self.word = " "
        self.current_symbol = "C"
        self.photo = "Empty"
        self.word1 = " "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "

        # Start video loop
        self.video_loop()

    # Main Video Loop for Real-Time Processing
    def video_loop(self):
        try:
            # Capturing and processing frame
            ok, frame = self.vs.read()
            cv2image = cv2.flip(frame, 1)
            if cv2image.any:
                hands = hd.findHands(cv2image, draw=False, flipType=True)
                cv2image_copy = np.array(cv2image)
                cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
                self.current_image = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=self.current_image)
                self.panel.imgtk = imgtk
                self.panel.config(image=imgtk)

                # Hand Detection and Landmark Extraction
                if hands[0]:
                    hand = hands[0]
                    map = hand[0]
                    x, y, w, h = map['bbox']
                    image = cv2image_copy[y - offset:y + h + offset, x - offset:x + w + offset]

                    white = cv2.imread("white.jpg")
                    if image.all:
                        handz = hd2.findHands(image, draw=False, flipType=True)
                        self.ccc += 1
                        if handz[0]:
                            hand = handz[0]
                            handmap = hand[0]
                            self.pts = handmap['lmList']

                            # Drawing Hand Landmarks and Skeleton
                            os = ((400 - w) // 2) - 15
                            os1 = ((400 - h) // 2) - 15
                            for t in range(0, 4, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                         (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(5, 8, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                         (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(9, 12, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                         (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(13, 16, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                         (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            for t in range(17, 20, 1):
                                cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                         (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                         (0, 255, 0), 3)
                            cv2.line(white, (self.pts[5][0] + os, self.pts[5][1] + os1),
                                     (self.pts[9][0] + os, self.pts[9][1] + os1),
                                     (0, 255, 0), 3)
                            cv2.line(white, (self.pts[9][0] + os, self.pts[9][1] + os1),
                                     (self.pts[13][0] + os, self.pts[13][1] + os1),
                                     (0, 255, 0), 3)
                            cv2.line(white, (self.pts[13][0] + os, self.pts[13][1] + os1),
                                     (self.pts[17][0] + os, self.pts[17][1] + os1),
                                     (0, 255, 0), 3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1),
                                     (self.pts[5][0] + os, self.pts[5][1] + os1),
                                     (0, 255, 0), 3)
                            cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1),
                                     (self.pts[17][0] + os, self.pts[17][1] + os1),
                                     (0, 255, 0), 3)

                            for i in range(21):
                                cv2.circle(white, (self.pts[i][0] + os, self.pts[i][1] + os1), 2, (0, 0, 255), 1)

                            # Character Prediction
                            res = white
                            self.predict(res)

                            # Updating GUI with Processed Image and Suggestions
                            self.current_image2 = Image.fromarray(res)
                            imgtk = ImageTk.PhotoImage(image=self.current_image2)
                            self.panel2.imgtk = imgtk
                            self.panel2.config(image=imgtk)
                            self.panel3.config(text=self.current_symbol, font=("Josefin Sans", 30))
                            self.b1.config(text=self.word1, font=("Josefin Sans", 20), wraplength=825,
                                           command=self.action1)
                            self.b2.config(text=self.word2, font=("Josefin Sans", 20), wraplength=825,
                                           command=self.action2)
                            self.b3.config(text=self.word3, font=("Josefin Sans", 20), wraplength=825,
                                           command=self.action3)
                            self.b4.config(text=self.word4, font=("Josefin Sans", 20), wraplength=825,
                                           command=self.action4)

                self.panel5.config(text=self.str, font=("Josefin Sans", 30), wraplength=1025)
        except Exception:
            # Exception Handling in Video Loop
            print(Exception.__traceback__)
            hands = hd.findHands(cv2image, draw=False, flipType=True)
            cv2image_copy = np.array(cv2image)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']
                image = cv2image_copy[y - offset:y + h + offset, x - offset:x + w + offset]

                white = cv2.imread(".\white.jpg")

                handz = hd2.findHands(image, draw=False, flipType=True)
                print(" ", self.ccc)
                self.ccc += 1
                if handz:
                    hand = handz[0]
                    self.pts = hand['lmList']

                    os = ((400 - w) // 2) - 15
                    os1 = ((400 - h) // 2) - 15
                    for t in range(0, 4, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                 (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(5, 8, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                 (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(9, 12, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                 (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(13, 16, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                 (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    for t in range(17, 20, 1):
                        cv2.line(white, (self.pts[t][0] + os, self.pts[t][1] + os1),
                                 (self.pts[t + 1][0] + os, self.pts[t + 1][1] + os1),
                                 (0, 255, 0), 3)
                    cv2.line(white, (self.pts[5][0] + os, self.pts[5][1] + os1),
                             (self.pts[9][0] + os, self.pts[9][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[9][0] + os, self.pts[9][1] + os1),
                             (self.pts[13][0] + os, self.pts[13][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[13][0] + os, self.pts[13][1] + os1),
                             (self.pts[17][0] + os, self.pts[17][1] + os1),
                             (0, 255, 0), 3)
                    cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1),
                             (self.pts[5][0] + os, self.pts[5][1] + os1), (0, 255, 0),
                             3)
                    cv2.line(white, (self.pts[0][0] + os, self.pts[0][1] + os1),
                             (self.pts[17][0] + os, self.pts[17][1] + os1), (0, 255, 0),
                             3)

                    for i in range(21):
                        cv2.circle(white, (self.pts[i][0] + os, self.pts[i][1] + os1), 2, (0, 0, 255), 1)

                    res = white
                    self.predict(res)

                    self.current_image2 = Image.fromarray(res)

                    imgtk = ImageTk.PhotoImage(image=self.current_image2)

                    self.panel2.imgtk = imgtk
                    self.panel2.config(image=imgtk)

                    self.panel3.config(text=self.current_symbol, font=("Josefin Sans", 30))

                    self.b1.config(text=self.word1, font=("Josefin Sans", 20), wraplength=825, command=self.action1)
                    self.b2.config(text=self.word2, font=("Josefin Sans", 20), wraplength=825, command=self.action2)
                    self.b3.config(text=self.word3, font=("Josefin Sans", 20), wraplength=825, command=self.action3)
                    self.b4.config(text=self.word4, font=("Josefin Sans", 20), wraplength=825, command=self.action4)

            self.panel5.config(text=self.str, font=("Josefin Sans", 30), wraplength=1025)
        except Exception:
            print("==", traceback.format_exc())
        finally:
            # Scheduling Next Frame
            self.root.after(1, self.video_loop)

    # Utility Function: Calculate Distance Between Two Points
    def distance(self, x, y):
        return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

    # Action: Update Character with Suggestion 1
    def action1(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word1.upper()

    # Action: Update Character with Suggestion 2
    def action2(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word2.upper()

    # Action: Update Character with Suggestion 3
    def action3(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word3.upper()

    # Action: Update Character with Suggestion 4
    def action4(self):
        idx_space = self.str.rfind(" ")
        idx_word = self.str.find(self.word, idx_space)
        last_idx = len(self.str)
        self.str = self.str[:idx_word]
        self.str = self.str + self.word4.upper()

    # Text-to-Speech: Speak the Converted Sentence
    def speak_fun(self):
        """Enhanced speak function with current voice settings"""
        if len(self.str.strip()) > 0:
            try:
                self.speak_engine.say(self.str)
                self.speak_engine.runAndWait()
            except Exception as e:
                print("Speech Error:", str(e))

    # Clear Function: Reset Text and Suggestions
    def clear_fun(self):
        self.str = " "
        self.word1 = " "
        self.word2 = " "
        self.word3 = " "
        self.word4 = " "
        self.panel5.config(text="")  # Clear English text
        self.panel6.config(text="")  # Clear translation

    # Add translation function
    def translate_fun(self):
        """Translate text to selected language"""
        if len(self.str.strip()) > 0:
            try:
                from googletrans import Translator
                translator = Translator()
                selected_lang = self.lang_var.get()
                lang_code = self.languages[selected_lang]
                translation = translator.translate(self.str, dest=lang_code)
                self.panel6.config(text=translation.text)
            except Exception as e:
                print("Translation error:", str(e))
                self.panel6.config(text="Translation error")

    # Predict Function: Recognize Sign Language from Image
    def predict(self, test_image):
        white = test_image
        white = white.reshape(1, 400, 400, 3)
        prob = np.array(self.model.predict(white)[0], dtype='float32')
        ch1 = np.argmax(prob, axis=0)
        prob[ch1] = 0
        ch2 = np.argmax(prob, axis=0)
        prob[ch2] = 0
        ch3 = np.argmax(prob, axis=0)
        prob[ch3] = 0

        pl = [ch1, ch2]

        l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
             [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
             [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
        if pl in l:
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 0

        l = [[2, 2], [2, 1]]
        if pl in l:
            if (self.pts[5][0] < self.pts[4][0]):
                ch1 = 0
                print("++++++++++++++++++")
        l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[0][0] > self.pts[8][0] and self.pts[0][0] > self.pts[4][0] and self.pts[0][0] > self.pts[12][
                0] and self.pts[0][0] > self.pts[16][0] and self.pts[0][0] > self.pts[20][0]) and self.pts[5][0] > \
                    self.pts[4][0]:
                ch1 = 2

        l = [[6, 0], [6, 6], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[8], self.pts[16]) < 52:
                ch1 = 2

        l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]

        if pl in l:
            if self.pts[6][1] > self.pts[8][1] and self.pts[14][1] < self.pts[16][1] and self.pts[18][1] < self.pts[20][
                1] and self.pts[0][0] < self.pts[8][0] and self.pts[0][0] < self.pts[12][0] and self.pts[0][0] < \
                    self.pts[16][0] and self.pts[0][0] < self.pts[20][0]:
                ch1 = 3

        l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][0] > self.pts[0][0]:
                ch1 = 3

        l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[2][1] + 15 < self.pts[16][1]:
                ch1 = 3

        l = [[6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[4], self.pts[11]) > 55:
                ch1 = 4

        l = [[1, 4], [1, 6], [1, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(self.pts[4], self.pts[11]) > 50) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] <
                    self.pts[20][1]):
                ch1 = 4

        l = [[3, 6], [3, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[4][0] < self.pts[0][0]):
                ch1 = 4

        l = [[2, 2], [2, 5], [2, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[1][0] < self.pts[12][0]):
                ch1 = 4

        l = [[2, 2], [2, 5], [2, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[1][0] < self.pts[12][0]):
                ch1 = 4

        l = [[3, 6], [3, 5], [3, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and self.pts[4][1] > self.pts[10][1]:
                ch1 = 5

        l = [[3, 2], [3, 1], [3, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][1] + 17 > self.pts[8][1] and self.pts[4][1] + 17 > self.pts[12][1] and self.pts[4][1] + 17 > \
                    self.pts[16][1] and self.pts[4][1] + 17 > self.pts[20][1]:
                ch1 = 5

        l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[4][0] > self.pts[0][0]:
                ch1 = 5

        l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[0][0] < self.pts[8][0] and self.pts[0][0] < self.pts[12][0] and self.pts[0][0] < self.pts[16][
                0] and self.pts[0][0] < self.pts[20][0]:
                ch1 = 5

        l = [[5, 7], [5, 2], [5, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[3][0] < self.pts[0][0]:
                ch1 = 7

        l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[6][1] < self.pts[8][1]:
                ch1 = 7

        l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[18][1] > self.pts[20][1]:
                ch1 = 7

        l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] > self.pts[16][0]:
                ch1 = 6

        print("2222  ch1=+++++++++++++++++", ch1, ",", ch2)
        l = [[7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[18][1] < self.pts[20][1] and self.pts[8][1] < self.pts[10][1]:
                ch1 = 6

        l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[8], self.pts[16]) > 50:
                ch1 = 6

        l = [[4, 6], [4, 2], [4, 1], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if self.distance(self.pts[4], self.pts[11]) < 60:
                ch1 = 6

        l = [[1, 4], [1, 6], [1, 0], [1, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] - self.pts[4][0] - 15 > 0:
                ch1 = 6

        l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0],
             [6, 3], [6, 4], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1],
             [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and
                    self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][1] and
                    self.pts[18][1] > self.pts[20][1]):
                ch1 = 1

        fg = 19
        l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                 self.pts[16][1] and
                 self.pts[18][1] < self.pts[20][1]) and (self.pts[2][0] < self.pts[0][0]) and self.pts[4][1] >
                    self.pts[14][1]):
                ch1 = 1

        l = [[4, 1], [4, 2], [4, 4]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.distance(self.pts[4], self.pts[11]) < 50) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] <
                    self.pts[20][1]):
                ch1 = 1

        l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                 self.pts[16][1] and
                 self.pts[18][1] < self.pts[20][1]) and (self.pts[2][0] < self.pts[0][0]) and self.pts[14][1] <
                    self.pts[4][1]):
                ch1 = 1

        l = [[6, 6], [6, 4], [6, 1], [6, 2]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[5][0] - self.pts[4][0] - 15 < 0:
                ch1 = 1

        l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                 self.pts[16][1] and
                 self.pts[18][1] > self.pts[20][1])):
                ch1 = 1

        l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
        pl = [ch1, ch2]
        if pl in l:
            if (self.pts[4][0] < self.pts[5][0] + 15) and (
                    (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                     self.pts[16][1] and
                     self.pts[18][1] > self.pts[20][1])):
                ch1 = 7

        l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if ((self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] <
                 self.pts[16][1] and
                 self.pts[18][1] < self.pts[20][1])) and self.pts[4][1] > self.pts[14][1]:
                ch1 = 1

        fg = 13
        l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
        pl = [ch1, ch2]
        if pl in l:
            if not (self.pts[0][0] + fg < self.pts[8][0] and self.pts[0][0] + fg < self.pts[12][0] and self.pts[0][
                0] + fg < self.pts[16][0] and
                    self.pts[0][0] + fg < self.pts[20][0]) and not (
                    self.pts[0][0] > self.pts[8][0] and self.pts[0][0] > self.pts[12][0] and self.pts[0][0] >
                    self.pts[16][0] and self.pts[0][0] > self.pts[20][0]) and self.distance(self.pts[4],
                                                                                            self.pts[11]) < 50:
                ch1 = 1

        l = [[5, 0], [5, 5], [0, 1]]
        pl = [ch1, ch2]
        if pl in l:
            if self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] > self.pts[16][
                1]:
                ch1 = 1

        if ch1 == 0:
            ch1 = 'S'
            if self.pts[4][0] < self.pts[6][0] and self.pts[4][0] < self.pts[10][0] and self.pts[4][0] < self.pts[14][
                0] and self.pts[4][0] < self.pts[18][0]:
                ch1 = 'A'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] < self.pts[10][0] and self.pts[4][0] < self.pts[14][
                0] and self.pts[4][0] < self.pts[18][0] and self.pts[4][1] < self.pts[14][1] and self.pts[4][1] < \
                    self.pts[18][1]:
                ch1 = 'T'
            if self.pts[4][1] > self.pts[8][1] and self.pts[4][1] > self.pts[12][1] and self.pts[4][1] > self.pts[16][
                1] and self.pts[4][1] > self.pts[20][1]:
                ch1 = 'E'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] > self.pts[10][0] and self.pts[4][0] > self.pts[14][
                0] and self.pts[4][1] < self.pts[18][1]:
                ch1 = 'M'
            if self.pts[4][0] > self.pts[6][0] and self.pts[4][0] > self.pts[10][0] and self.pts[4][1] < self.pts[18][
                1] and self.pts[4][1] < self.pts[14][1]:
                ch1 = 'N'

        if ch1 == 2:
            if self.distance(self.pts[12], self.pts[4]) > 42:
                ch1 = 'C'
            else:
                ch1 = 'O'

        if ch1 == 3:
            if (self.distance(self.pts[8], self.pts[12])) > 72:
                ch1 = 'G'
            else:
                ch1 = 'H'

        if ch1 == 7:
            if self.distance(self.pts[8], self.pts[4]) > 42:
                ch1 = 'Y'
            else:
                ch1 = 'J'

        if ch1 == 4:
            ch1 = 'L'

        if ch1 == 6:
            ch1 = 'X'

        if ch1 == 5:
            if self.pts[4][0] > self.pts[12][0] and self.pts[4][0] > self.pts[16][0] and self.pts[4][0] > self.pts[20][
                0]:
                if self.pts[8][1] < self.pts[5][1]:
                    ch1 = 'Z'
                else:
                    ch1 = 'Q'
            else:
                ch1 = 'P'

        if ch1 == 1:
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'B'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'D'
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'F'
            if (self.pts[6][1] < self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = 'I'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and self.pts[18][1] < self.pts[20][1]):
                ch1 = 'W'
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] <
                self.pts[16][1] and self.pts[18][1] < self.pts[20][1]) and self.pts[4][1] < self.pts[9][1]:
                ch1 = 'K'
            if ((self.distance(self.pts[8], self.pts[12]) - self.distance(self.pts[6], self.pts[10])) < 8) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] <
                    self.pts[20][1]):
                ch1 = 'U'
            if ((self.distance(self.pts[8], self.pts[12]) - self.distance(self.pts[6], self.pts[10])) >= 8) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] <
                    self.pts[20][1]) and (self.pts[4][1] > self.pts[9][1]):
                ch1 = 'V'

            if (self.pts[8][0] > self.pts[12][0]) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] <
                    self.pts[20][1]):
                ch1 = 'R'

        if ch1 == 1 or ch1 == 'E' or ch1 == 'S' or ch1 == 'X' or ch1 == 'Y' or ch1 == 'B':
            if (self.pts[6][1] > self.pts[8][1] and self.pts[10][1] < self.pts[12][1] and self.pts[14][1] <
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = " "

        print(self.pts[4][0] < self.pts[5][0])
        if ch1 == 'E' or ch1 == 'Y' or ch1 == 'B':
            if (self.pts[4][0] < self.pts[5][0]) and (
                    self.pts[6][1] > self.pts[8][1] and self.pts[10][1] > self.pts[12][1] and self.pts[14][1] >
                    self.pts[16][1] and self.pts[18][1] > self.pts[20][1]):
                ch1 = "next"

        if ch1 == 'Next' or 'B' or 'C' or 'H' or 'F' or 'X':
            if (self.pts[0][0] > self.pts[8][0] and self.pts[0][0] > self.pts[12][0] and self.pts[0][0] > self.pts[16][
                0] and self.pts[0][0] > self.pts[20][0]) and (
                    self.pts[4][1] < self.pts[8][1] and self.pts[4][1] < self.pts[12][1] and self.pts[4][1] <
                    self.pts[16][1] and self.pts[4][1] < self.pts[20][1]) and (
                    self.pts[4][1] < self.pts[6][1] and self.pts[4][1] < self.pts[10][1] and self.pts[4][1] <
                    self.pts[14][1] and self.pts[4][1] < self.pts[18][1]):
                ch1 = 'Backspace'

        if ch1 == "next" and self.prev_char != "next":
            if self.ten_prev_char[(self.count - 2) % 10] != "next":
                if self.ten_prev_char[(self.count - 2) % 10] == "Backspace":
                    self.str = self.str[0:-1]
                else:
                    if self.ten_prev_char[(self.count - 2) % 10] != "Backspace":
                        self.str = self.str + self.ten_prev_char[(self.count - 2) % 10]
            else:
                if self.ten_prev_char[(self.count - 0) % 10] != "Backspace":
                    self.str = self.str + self.ten_prev_char[(self.count - 0) % 10]

        if ch1 == "  " and self.prev_char != "  ":
            self.str = self.str + "  "

        self.prev_char = ch1
        self.current_symbol = ch1
        self.count += 1
        self.ten_prev_char[self.count % 10] = ch1

        if len(self.str.strip()) != 0:
            st = self.str.rfind(" ")
            ed = len(self.str)
            word = self.str[st + 1:ed]
            self.word = word
            if len(word.strip()) != 0:
                ddd.check(word)
                lenn = len(ddd.suggest(word))
                if lenn >= 4:
                    self.word4 = ddd.suggest(word)[3]

                if lenn >= 3:
                    self.word3 = ddd.suggest(word)[2]

                if lenn >= 2:
                    self.word2 = ddd.suggest(word)[1]

                if lenn >= 1:
                    self.word1 = ddd.suggest(word)[0]
            else:
                self.word1 = " "
                self.word2 = " "
                self.word3 = " "
                self.word4 = " "

    def speak_regional_fun(self):
        """Function to convert regional language text to speech"""
        if len(self.panel6.cget("text").strip()) > 0:
            try:
                from gtts import gTTS
                import os
                import pygame
                
                selected_lang = self.lang_var.get()
                lang_code = self.languages[selected_lang]
                
                # Create speech in selected language
                tts = gTTS(text=self.panel6.cget("text"), lang=lang_code)
                tts.save("regional_speech.mp3")
                
                # Initialize pygame mixer
                pygame.mixer.init()
                pygame.mixer.music.load("regional_speech.mp3")
                pygame.mixer.music.play()
                
                # Wait for the audio to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
                # Cleanup
                pygame.mixer.quit()
                os.remove("regional_speech.mp3")
            except Exception as e:
                print("Regional Speech Error:", str(e))

    def on_language_change(self, event=None):
        """Update the translation label when language changes"""
        selected = self.lang_var.get()
        # Extract the language name before the parentheses
        lang_name = selected.split(" (")[0]
        self.T5.config(text=f"{lang_name}:")
        # Retranslate if there's existing text
        if len(self.str.strip()) > 0:
            self.translate_fun()

    def on_voice_change(self, event=None):
        """Update the voice when selection changes"""
        selected_idx = self.voice_dropdown.current()
        self.current_voice = self.voices[selected_idx]
        self.speak_engine.setProperty("voice", self.current_voice.id)

    def on_rate_change(self, event=None):
        """Update the speech rate"""
        new_rate = self.rate_scale.get()
        self.speak_engine.setProperty("rate", new_rate)

    def on_volume_change(self, event=None):
        """Update the speech volume"""
        new_volume = self.volume_scale.get()
        self.speak_engine.setProperty("volume", new_volume)

    # Destructor: Clean Up Resources and Close Application
    def destructor(self):
        print(self.ten_prev_char)
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


# Start the Application
print("Starting Application...")
(Application()).root.mainloop()